from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, get, replace_in_file, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
from conans import tools as tools_legacy
import os
import shutil

required_conan_version = ">=1.50.0"


class GLibConan(ConanFile):
    name = "glib"
    description = "GLib provides the core application building blocks for libraries and applications written in C"
    topics = ("glib", "gobject", "gio", "gmodule")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.gnome.org/GNOME/glib"
    license = "LGPL-2.1"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_pcre": [True, False],
        "with_elf": [True, False],
        "with_selinux": [True, False],
        "with_mount": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_pcre": True,
        "with_elf": True,
        "with_mount": True,
        "with_selinux": True,
    }

    short_paths = True

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            if Version(self.version) < "2.71.1":
                self.options.shared = True
        if self.settings.os != "Linux":
            del self.options.with_mount
            del self.options.with_selinux
        if is_msvc(self):
            del self.options.with_elf

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
           del self.settings.compiler.libcxx
        except Exception:
           pass
        try:
           del self.settings.compiler.cppstd
        except Exception:
           pass

    def requirements(self):
        self.requires("zlib/1.2.12")
        self.requires("libffi/3.4.2")
        if self.options.with_pcre:
            if Version(self.version) >= "2.73.2":
                self.requires("pcre2/10.40")
            else:
                self.requires("pcre/8.45")
        if self.options.get_safe("with_elf"):
            self.requires("libelf/0.8.13")
        if self.options.get_safe("with_mount"):
            self.requires("libmount/2.36.2")
        if self.options.get_safe("with_selinux"):
            self.requires("libselinux/3.3")
        if self.settings.os != "Linux":
            # for Linux, gettext is provided by libc
            self.requires("libgettext/0.21")

        if tools_legacy.is_apple_os(self.settings.os):
            self.requires("libiconv/1.17")

    def validate(self):
        if Version(self.version) >= "2.69.0" and not self.options.with_pcre:
            raise ConanInvalidConfiguration("option glib:with_pcre must be True for glib >= 2.69.0")
        if self.settings.os == "Windows" and not self.options.shared and Version(self.version) < "2.71.1":
            raise ConanInvalidConfiguration(
                "glib < 2.71.1 can not be built as static library on Windows. "
                "see https://gitlab.gnome.org/GNOME/glib/-/issues/692"
            )
        if Version(self.version) < "2.67.0" and not is_msvc(self) and not self.options.with_elf:
            raise ConanInvalidConfiguration("libelf dependency can't be disabled in glib < 2.67.0")

    def build_requirements(self):
        self.tool_requires("meson/0.63.1")
        self.tool_requires("pkgconf/1.7.4")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        if tools_legacy.is_apple_os(self.settings.os):
            tc.project_options["iconv"] = "external"  # https://gitlab.gnome.org/GNOME/glib/issues/1557
        tc.project_options["selinux"] = "enabled" if self.options.get_safe("with_selinux") else "disabled"
        tc.project_options["libmount"] = "enabled" if self.options.get_safe("with_mount") else "disabled"
        if Version(self.version) < "2.69.0":
            tc.project_options["internal_pcre"] = not self.options.with_pcre
        if self.settings.os == "FreeBSD":
            tc.project_options["xattr"] = "false"
        if Version(self.version) >= "2.67.2":
            tc.project_options["tests"] = "false"
        if Version(self.version) >= "2.67.0":
            tc.project_options["libelf"] = "enabled" if self.options.get_safe("with_elf") else "disabled"
        # TODO: fixed in conan 1.51.0?
        tc.project_options["bindir"] = "bin"
        tc.project_options["libdir"] = "lib"
        tc.generate()

        pkg = PkgConfigDeps(self)
        pkg.generate()

        buildenv = VirtualBuildEnv(self)
        buildenv.generate(scope="build")

    def _patch_sources(self):
        apply_conandata_patches(self)
        meson_build = os.path.join(self.source_folder, "meson.build")
        if Version(self.version) < "2.67.2":
            replace_in_file(self,
                meson_build,
                "build_tests = not meson.is_cross_build() or (meson.is_cross_build() and meson.has_exe_wrapper())",
                "build_tests = false",
            )
        replace_in_file(self,
            meson_build,
            "subdir('fuzzing')",
            "#subdir('fuzzing')",
        )  # https://gitlab.gnome.org/GNOME/glib/-/issues/2152
        if Version(self.version) < "2.73.2":
            for filename in [
                meson_build,
                os.path.join(self.source_folder, "glib", "meson.build"),
                os.path.join(self.source_folder, "gobject", "meson.build"),
                os.path.join(self.source_folder, "gio", "meson.build"),
            ]:
                replace_in_file(self, filename, "subdir('tests')", "#subdir('tests')")
        if self.settings.os != "Linux":
            # allow to find gettext
            replace_in_file(self,
                meson_build,
                "libintl = cc.find_library('intl', required : false)" if Version(self.version) < "2.73.1" \
                else "libintl = dependency('intl', required: false)",
                "libintl = dependency('libgettext', method : 'pkg-config', required : false)",
            )

        replace_in_file(self,
            os.path.join(
                self.source_folder,
                "gio",
                "gdbus-2.0",
                "codegen",
                "gdbus-codegen.in",
            ),
            "'share'",
            "'res'",
        )
        if self.settings.os != "Linux":
            replace_in_file(self,
                meson_build,
                "if cc.has_function('ngettext'",
                "if false #cc.has_function('ngettext'",
            )

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        if Version(self.version) < "2.73.0":
            copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        else:
            copy(self, "LGPL-2.1-or-later.txt", src=os.path.join(self.source_folder, "LICENSES"),
                                                dst=os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        shutil.move(
            os.path.join(self.package_folder, "share"),
            os.path.join(self.package_folder, "res"),
        )
        fix_apple_shared_install_name(self)
        fix_msvc_libname(self)

    def package_info(self):
        self.cpp_info.components["glib-2.0"].libs = ["glib-2.0"]
        self.cpp_info.components["glib-2.0"].names["pkg_config"] = "glib-2.0"
        self.cpp_info.components["glib-2.0"].set_property("pkg_config_name", "glib-2.0")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["glib-2.0"].system_libs.append("pthread")
        if self.settings.os == "Windows":
            self.cpp_info.components["glib-2.0"].system_libs.extend(
                ["ws2_32", "ole32", "shell32", "user32", "advapi32"]
            )
        if self.settings.os == "Macos":
            self.cpp_info.components["glib-2.0"].system_libs.append("resolv")
            self.cpp_info.components["glib-2.0"].frameworks.extend(
                ["Foundation", "CoreServices", "CoreFoundation"]
            )
        self.cpp_info.components["glib-2.0"].includedirs.append(
            os.path.join("include", "glib-2.0")
        )
        self.cpp_info.components["glib-2.0"].includedirs.append(
            os.path.join("lib", "glib-2.0", "include")
        )
        if self.options.with_pcre:
            if Version(self.version) >= "2.73.2":
                self.cpp_info.components["glib-2.0"].requires.append("pcre2::pcre2")
            else:
                self.cpp_info.components["glib-2.0"].requires.append("pcre::pcre")
        if self.settings.os != "Linux":
            self.cpp_info.components["glib-2.0"].requires.append(
                "libgettext::libgettext"
            )
        if tools_legacy.is_apple_os(self.settings.os):
            self.cpp_info.components["glib-2.0"].requires.append("libiconv::libiconv")

        self.cpp_info.components["gmodule-no-export-2.0"].libs = ["gmodule-2.0"]
        self.cpp_info.components["gmodule-no-export-2.0"].set_property("pkg_config_name", "gmodule-no-export-2.0")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["gmodule-no-export-2.0"].system_libs.append(
                "pthread"
            )
            self.cpp_info.components["gmodule-no-export-2.0"].system_libs.append("dl")
        self.cpp_info.components["gmodule-no-export-2.0"].requires.append("glib-2.0")

        self.cpp_info.components["gmodule-export-2.0"].requires.extend(
            ["gmodule-no-export-2.0", "glib-2.0"]
        )
        self.cpp_info.components["gmodule-export-2.0"].set_property("pkg_config_name", "gmodule-export-2.0")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["gmodule-export-2.0"].sharedlinkflags.append(
                "-Wl,--export-dynamic"
            )

        self.cpp_info.components["gmodule-2.0"].set_property("pkg_config_name", "gmodule-2.0")
        self.cpp_info.components["gmodule-2.0"].requires.extend(
            ["gmodule-no-export-2.0", "glib-2.0"]
        )
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["gmodule-2.0"].sharedlinkflags.append(
                "-Wl,--export-dynamic"
            )

        self.cpp_info.components["gobject-2.0"].set_property("pkg_config_name", "gobject-2.0")
        self.cpp_info.components["gobject-2.0"].libs = ["gobject-2.0"]
        self.cpp_info.components["gobject-2.0"].requires.append("glib-2.0")
        self.cpp_info.components["gobject-2.0"].requires.append("libffi::libffi")

        self.cpp_info.components["gthread-2.0"].set_property("pkg_config_name", "gthread-2.0")
        self.cpp_info.components["gthread-2.0"].libs = ["gthread-2.0"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["gthread-2.0"].system_libs.append("pthread")
        self.cpp_info.components["gthread-2.0"].requires.append("glib-2.0")

        self.cpp_info.components["gio-2.0"].set_property("pkg_config_name", "gio-2.0")
        self.cpp_info.components["gio-2.0"].libs = ["gio-2.0"]
        if self.settings.os == "Linux":
            self.cpp_info.components["gio-2.0"].system_libs.append("resolv")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["gio-2.0"].system_libs.append("dl")
        if self.settings.os == "Windows":
            self.cpp_info.components["gio-2.0"].system_libs.extend(["iphlpapi", "dnsapi", "shlwapi"])
        self.cpp_info.components["gio-2.0"].requires.extend(
            ["glib-2.0", "gobject-2.0", "gmodule-2.0", "zlib::zlib"]
        )
        if self.settings.os == "Macos":
            self.cpp_info.components["gio-2.0"].frameworks.append("AppKit")
        if self.options.get_safe("with_mount"):
            self.cpp_info.components["gio-2.0"].requires.append("libmount::libmount")
        if self.options.get_safe("with_selinux"):
            self.cpp_info.components["gio-2.0"].requires.append(
                "libselinux::libselinux"
            )
        if self.settings.os == "Windows":
            self.cpp_info.components["gio-windows-2.0"].requires = [
                "gobject-2.0",
                "gmodule-no-export-2.0",
                "gio-2.0",
            ]
            self.cpp_info.components["gio-windows-2.0"].includedirs = [
                os.path.join("include", "gio-win32-2.0")
            ]
        else:
            self.cpp_info.components["gio-unix-2.0"].requires.extend(
                ["gobject-2.0", "gio-2.0"]
            )
            self.cpp_info.components["gio-unix-2.0"].includedirs = [
                os.path.join("include", "gio-unix-2.0")
            ]
        self.env_info.GLIB_COMPILE_SCHEMAS = os.path.join(
            self.package_folder, "bin", "glib-compile-schemas"
        )

        self.cpp_info.components["gresource"].set_property("pkg_config_name", "gresource")
        self.cpp_info.components["gresource"].libs = []  # this is actually an executable
        if self.options.get_safe("with_elf"):
            self.cpp_info.components["gresource"].requires.append(
                "libelf::libelf"
            )  # this is actually an executable

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH env var with: {bin_path}")
        self.env_info.PATH.append(bin_path)

        pkgconfig_variables = {
            'datadir': '${prefix}/res',
            'schemasdir': '${datadir}/glib-2.0/schemas',
            'bindir': '${prefix}/bin',
            'giomoduledir': '${libdir}/gio/modules',
            'gio': '${bindir}/gio',
            'gio_querymodules': '${bindir}/gio-querymodules',
            'glib_compile_schemas': '${bindir}/glib-compile-schemas',
            'glib_compile_resources': '${bindir}/glib-compile-resources',
            'gdbus': '${bindir}/gdbus',
            'gdbus_codegen': '${bindir}/gdbus-codegen',
            'gresource': '${bindir}/gresource',
            'gsettings': '${bindir}/gsettings'
        }
        self.cpp_info.components["gio-2.0"].set_property(
            "pkg_config_custom_content",
            "\n".join(f"{key}={value}" for key,value in pkgconfig_variables.items()))

        pkgconfig_variables = {
            'bindir': '${prefix}/bin',
            'glib_genmarshal': '${bindir}/glib-genmarshal',
            'gobject_query': '${bindir}/gobject-query',
            'glib_mkenums': '${bindir}/glib-mkenums'
        }
        self.cpp_info.components["glib-2.0"].set_property(
            "pkg_config_custom_content",
            "\n".join(f"{key}={value}" for key,value in pkgconfig_variables.items()))

def fix_msvc_libname(conanfile):
    """remove lib prefix & change extension to .lib"""
    from conan.tools.files import rename
    import glob
    if not is_msvc(conanfile):
        return
    libdirs = getattr(conanfile.cpp.package, "libdirs")
    for libdir in libdirs:
        for ext in [".dll.a", ".dll.lib", ".a"]:
            full_folder = os.path.join(conanfile.package_folder, libdir)
            for filepath in glob.glob(os.path.join(full_folder, f"*{ext}")):
                libname = os.path.splitext(os.path.basename(filepath))[0]
                if libname[0:3] == "lib":
                    libname = libname[3:]
                rename(conanfile, filepath, os.path.join(os.path.dirname(filepath), f"{libname}.lib"))
