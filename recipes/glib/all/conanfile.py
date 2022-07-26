import glob
import os
import re

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple.apple import is_apple_os
from conan.tools.files import apply_conandata_patches, chdir, get, load, rename, replace_in_file, rmdir, save
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
from conans.tools import remove_files_by_mask

required_conan_version = ">=1.47.0"


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
        "with_mount": [True, False],
        "with_selinux": [True, False],
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
    generators = "PkgConfigDeps", "VirtualBuildEnv", "VirtualRunEnv"

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

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

        if is_apple_os(self.settings.os):
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
        self.tool_requires("meson/0.62.2")
        self.tool_requires("pkgconf/1.7.4")

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["libdir"] = "lib"
        tc.project_options["localedir"] = "res"
        tc.project_options["datadir"] = "res"
        if is_apple_os(self.settings.os):
            tc.project_options["iconv"] = "external"  # https://gitlab.gnome.org/GNOME/glib/issues/1557
        tc.project_options["selinux"] = "enabled" if self.options.get_safe("with_selinux") else "disabled"
        tc.project_options["libmount"] = "enabled" if self.options.get_safe("with_mount") else "disabled"

        if Version(self.version) < "2.69.0":
            tc.project_options["internal_pcre"] = not self.options.with_pcre

        if self.settings.os == "FreeBSD":
            tc.project_options["xattr"] = False
        if Version(self.version) >= "2.67.2":
            tc.project_options["tests"] = False

        if Version(self.version) >= "2.67.0":
            tc.project_options["libelf"] = "enabled" if self.options.get_safe("with_elf") else "disabled"

        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if Version(self.version) < "2.67.2":
            replace_in_file(
                self,
                os.path.join(self.source_folder, "meson.build"),
                "build_tests = not meson.is_cross_build() or (meson.is_cross_build() and meson.has_exe_wrapper())",
                "build_tests = false",
            )
        replace_in_file(
            self,
            os.path.join(self.source_folder, "meson.build"),
            "subdir('fuzzing')",
            "#subdir('fuzzing')",
        )  # https://gitlab.gnome.org/GNOME/glib/-/issues/2152
        if Version(self.version) < "2.73.2":
            for filename in [
                os.path.join(self.source_folder, "meson.build"),
                os.path.join(self.source_folder, "glib", "meson.build"),
                os.path.join(self.source_folder, "gobject", "meson.build"),
                os.path.join(self.source_folder, "gio", "meson.build"),
            ]:
                replace_in_file(self, filename, "subdir('tests')", "#subdir('tests')")
        if self.settings.os != "Linux":
            # allow to find gettext
            replace_in_file(
                self,
                os.path.join(self.source_folder, "meson.build"),
                "libintl = cc.find_library('intl', required : false)" if Version(self.version) < "2.73.1" \
                else "libintl = dependency('intl', required: false)",
                "libintl = dependency('libgettext', method : 'pkg-config', required : false)",
            )

        replace_in_file(
            self,
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
            replace_in_file(
                self,
                os.path.join(self.source_folder, "meson.build"),
                "if cc.has_function('ngettext'",
                "if false #cc.has_function('ngettext'",
            )

    def _patch_pkgconfig(self):
        with chdir(self, self.generators_folder):
            for filename in glob.glob("*.pc"):
                self.output.info(f"processing {filename}")
                content = load(self, filename)
                results = re.findall(r"-F (.*)[ \n]", content)
                for result in results:
                    if not os.path.isdir(result):
                        self.output.info(f"removing bad framework path {result}")
                        content = content.replace(f"-F {result}", "")
                save(self, filename, content)

    def build(self):
        self._patch_sources()
        self._patch_pkgconfig()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def _fix_library_names(self):
        if self.settings.compiler == "Visual Studio":
            with chdir(self, os.path.join(self.package_folder, "lib")):
                for filename_old in glob.glob("*.a"):
                    filename_new = filename_old[3:-2] + ".lib"
                    self.output.info(f"rename {filename_old} into {filename_new}")
                    rename(self, filename_old, filename_new)

    def package(self):
        if Version(self.version) < "2.73.0":
            self.copy(pattern="COPYING", dst="licenses", src=self.source_folder)
        else:
            self.copy(pattern="LGPL-2.1-or-later.txt", dst="licenses", src=os.path.join(self.source_folder, "LICENSES"))
        meson = Meson(self)
        meson.install()
        self._fix_library_names()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        for pdb_file in glob.glob(os.path.join(self.package_folder, "bin", "*.pdb")):
            os.unlink(pdb_file)
        remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.pdb")
        remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.pc")

    def package_info(self):
        self.cpp_info.components["glib-2.0"].libs = ["glib-2.0"]
        self.cpp_info.components["glib-2.0"].names["pkg_config"] = "glib-2.0"
        self.cpp_info.components["glib-2.0"].set_property("pkg_config_name", "glib-2.0")

        # todo Remove when using Conan 1.50.0.
        self.cpp_info.components["glib-2.0"].libdirs = ["lib"]

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
        if is_apple_os(self.settings.os):
            self.cpp_info.components["glib-2.0"].requires.append("libiconv::libiconv")

        self.cpp_info.components["gmodule-no-export-2.0"].libs = ["gmodule-2.0"]
        self.cpp_info.components["gmodule-no-export-2.0"].set_property("pkg_config_name", "gmodule-no-export-2.0")

        # todo Remove when using Conan 1.50.0.
        self.cpp_info.components["gmodule-no-export-2.0"].libdirs = ["lib"]

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

        # todo Remove when using Conan 1.50.0.
        self.cpp_info.components["gobject-2.0"].libdirs = ["lib"]

        self.cpp_info.components["gobject-2.0"].requires.append("glib-2.0")
        self.cpp_info.components["gobject-2.0"].requires.append("libffi::libffi")

        self.cpp_info.components["gthread-2.0"].set_property("pkg_config_name", "gthread-2.0")
        self.cpp_info.components["gthread-2.0"].libs = ["gthread-2.0"]

        # todo Remove when using Conan 1.50.0.
        self.cpp_info.components["gthread-2.0"].libdirs = ["lib"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["gthread-2.0"].system_libs.append("pthread")
        self.cpp_info.components["gthread-2.0"].requires.append("glib-2.0")

        self.cpp_info.components["gio-2.0"].set_property("pkg_config_name", "gio-2.0")
        self.cpp_info.components["gio-2.0"].libs = ["gio-2.0"]

        # todo Remove when using Conan 1.50.0.
        self.cpp_info.components["gio-2.0"].libdirs = ["lib"]

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

            # todo Remove when using Conan 1.50.0.
            self.cpp_info.components["gio-windows-2.0"].libdirs = ["lib"]
        else:
            self.cpp_info.components["gio-unix-2.0"].requires.extend(
                ["gobject-2.0", "gio-2.0"]
            )
            self.cpp_info.components["gio-unix-2.0"].includedirs = [
                os.path.join("include", "gio-unix-2.0")
            ]

            # todo Remove when using Conan 1.50.0.
            self.cpp_info.components["gio-unix-2.0"].libdirs = ["lib"]

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
        self.output.info(f"Prepending PATH env var with: {bin_path}")
        self.runenv_info.prepend_path("PATH", bin_path)

        pkgconfig_variables = {
            'datadir': '${prefix}/res',
            'schemasdir': '${datadir}/glib-2.0/schemas',
            'bindir': '${prefix}/bin',
            'libdir': '${prefix}/lib',
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
