import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
    replace_in_file,
    rename,
    rm,
    rmdir
)
from conan.tools.gnu import PkgConfigDeps, Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.scm import Version

required_conan_version = ">=1.54.0"


class CairoConan(ConanFile):
    name = "cairo"
    description = "Cairo is a 2D graphics library with support for multiple output devices"
    topics = ("cairo", "graphics")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://cairographics.org/"
    license = ("LGPL-2.1-only", "MPL-1.1")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_freetype": [True, False],
        "with_fontconfig": [True, False],
        "with_xlib": [True, False],
        "with_xlib_xrender": [True, False],
        "with_xcb": [True, False],
        "with_glib": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_freetype": True,
        "with_fontconfig": True,
        "with_xlib": True,
        "with_xlib_xrender": False,
        "with_xcb": True,
        "with_glib": True,
    }
    short_paths = True

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.with_fontconfig
        if is_msvc(self):
            del self.options.with_freetype
            del self.options.with_glib
        if self.settings.os != "Linux":
            del self.options.with_xlib
            del self.options.with_xlib_xrender
            del self.options.with_xcb

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.get_safe("with_freetype", True):
            self.requires("freetype/2.13.0")
        if self.options.get_safe("with_fontconfig", False):
            self.requires("fontconfig/2.13.93")
        if self.settings.os == "Linux":
            if self.options.with_xlib or self.options.with_xlib_xrender or self.options.with_xcb:
                self.requires("xorg/system")
        if self.options.get_safe("with_glib", True):
            self.requires("glib/2.76.1")
        self.requires("zlib/1.2.13")
        self.requires("pixman/0.40.0")
        self.requires("libpng/1.6.39")

    def package_id(self):
        if self.options.get_safe("with_glib") and not self.dependencies["glib"].options.shared:
            self.info.requires["glib"].full_package_mode()

    def validate(self):
        if is_msvc(self):
            # TODO autotools build results in LNK1127 error from a library in the WindowsSDK on CCI
            #  should be retested in case this is just a CCI environment issue
            raise ConanInvalidConfiguration("MSVC autotools build is not supported. Use the Meson build instead.")

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/1.9.3")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", default=False, check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("automake/1.16.5")
        else:
            self.tool_requires("gtk-doc-stub/cci.20181216")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _create_toolchain(self, namespace, directory):
        def is_enabled(value):
            return "yes" if value else "no"

        def dep_path(dependency):
            return unix_path(self, self.deps_cpp_info[dependency].rootpath)

        tc = AutotoolsToolchain(self, namespace=namespace)
        tc.configure_args += [
            f"--datarootdir={unix_path(self, os.path.join(self.package_folder, 'res'))}",
            f"--enable-ft={is_enabled(self.options.get_safe('with_freetype', True))}",
            f"--enable-gobject={is_enabled(self.options.get_safe('with_glib', True))}",
            f"--enable-fc={is_enabled(self.options.get_safe('with_fontconfig'))}",
            f"--enable-xlib={is_enabled(self.options.get_safe('with_xlib'))}",
            f"--enable-xlib_xrender={is_enabled(self.options.get_safe('with_xlib_xrender'))}",
            f"--enable-xcb={is_enabled(self.options.get_safe('xcb'))}",
            "--disable-gtk-doc"
        ]
        if is_msvc(self):
            tc.make_args +=  [
                "--directory", directory,
                "-f", "Makefile.win32",
                f"CFG={str(self.settings.build_type).lower()}",
                "CAIRO_HAS_FC_FONT=0",
                f"ZLIB_PATH={dep_path('zlib')}",
                f"LIBPNG_PATH={dep_path('libpng')}",
                f"PIXMAN_PATH={dep_path('pixman')}",
                f"FREETYPE_PATH={dep_path('freetype')}",
                f"GOBJECT_PATH={dep_path('glib')}"
            ]
            tc.extra_cflags += ["-FS"]

        if self.settings.compiler in ["gcc", "clang", "apple-clang"]:
            tc.extra_cflags.append("-Wno-enum-conversion")

        return tc

    def generate(self):
        VirtualBuildEnv(self).generate()

        if not cross_building(self):
            VirtualRunEnv(self).generate(scope="build")

        tc_main = self._create_toolchain("main", unix_path(self, self.source_folder))
        tc_main.generate()

        if is_msvc(self):
            tc_gobject = self._create_toolchain("gobject", unix_path(self, os.path.join(self.source_folder, "util", "cairo-gobject")))
            tc_gobject.generate()

        PkgConfigDeps(self).generate()
        deps = AutotoolsDeps(self)
        if is_msvc(self):
            cppflags = deps.vars().get("CPPFLAGS")
            deps.environment.append('CFLAGS', cppflags.replace("/I", "-I"))
            ldflags = deps.vars().get("LDFLAGS")
            deps.environment.define('LDFLAGS', ldflags.replace("/LIBPATH:", "-LIBPATH:"))
            deps.environment.append('LDFLAGS', deps.vars().get("LIBS"))

        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        def fix_freetype_version():
            replace_in_file(
                self,
                os.path.join(self.source_folder, "configure.ac"),
                "FREETYPE_MIN_VERSION=9.7.3",
                f"FREETYPE_MIN_VERSION={Version(self.dependencies['freetype'].ref.version)}"
            )

        def exclude_tests_and_docs_from_build():
            makefile_am = os.path.join(self.source_folder, "Makefile.am")
            replace_in_file(self, makefile_am, "SUBDIRS += boilerplate test perf", "")
            replace_in_file(self, makefile_am, "SUBDIRS = src doc util", "SUBDIRS = src util")

        fix_freetype_version()
        exclude_tests_and_docs_from_build()

        if self.options.get_safe("with_freetype"):
            replace_in_file(self, os.path.join(self.source_folder, "src", "cairo-ft-font.c"),
                                  "#if HAVE_UNISTD_H", "#ifdef HAVE_UNISTD_H")

        if is_msvc(self):
            # https://cairographics.org/end_to_end_build_for_win32/
            win32_common = os.path.join(self.source_folder, "build", "Makefile.win32.common")
            replace_in_file(self, win32_common, "-MD ", f"-{self.settings.compiler.runtime} ")
            replace_in_file(self, win32_common, "-MDd ", f"-{self.settings.compiler.runtime} ")
            replace_in_file(self, win32_common, "$(PIXMAN_PATH)/lib/pixman-1.lib",
                            self.deps_cpp_info["pixman"].libs[0] + ".lib")
            replace_in_file(self, win32_common, "$(FREETYPE_PATH)/lib/freetype.lib",
                            self.deps_cpp_info["freetype"].libs[0] + ".lib")
            replace_in_file(self, win32_common, "$(ZLIB_PATH)/lib/zlib1.lib",
                            self.deps_cpp_info["zlib"].libs[0] + ".lib")
            replace_in_file(self, win32_common, "$(LIBPNG_PATH)/lib/libpng16.lib",
                            self.deps_cpp_info["libpng"].libs[0] + ".lib")

    def build(self):
        self._patch_sources()
        autotools = Autotools(self, namespace="main")
        if is_msvc(self):
            autotools.make()
            autotools_gobject = Autotools(self, namespace="gobject")
            autotools_gobject.make()
        else:
            autotools.autoreconf()
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if is_msvc(self):
            src = os.path.join(self.source_folder, "src")
            inc = os.path.join(self.package_folder, "include", "cairo")
            copy(self, "cairo-version.h", (src if Version(self.version) >= "1.17.4" else self.source_folder), inc)
            copy(self, "cairo-features.h", src, inc)
            copy(self, "cairo.h", src, inc)
            copy(self, "cairo-deprecated.h", src, inc)
            copy(self, "cairo-win32.h", src, inc)
            copy(self, "cairo-script.h", src, inc)
            copy(self, "cairo-ft.h", src, inc)
            copy(self, "cairo-ps.h", src, inc)
            copy(self, "cairo-pdf.h", src, inc)
            copy(self, "cairo-svg.h", src, inc)
            copy(self, "cairo-gobject.h", inc, os.path.join(self.source_folder, "util", "cairo-gobject"))

            config = str(self.settings.build_type).lower()
            lib_src_path = os.path.join(self.source_folder, "src", config)
            cairo_gobject_src_path = os.path.join(self.source_folder, "util", "cairo-gobject", config)
            lib_dest_path = os.path.join(self.package_folder, "lib")
            runtime_dest_path = os.path.join(self.package_folder, "bin")

            if self.options.shared:
                copy(self, "*cairo.lib", lib_src_path, lib_dest_path)
                copy(self, "*cairo.dll", lib_src_path, runtime_dest_path)
                copy(self, "*cairo-gobject.lib", cairo_gobject_src_path, lib_dest_path)
                copy(self, "*cairo-gobject.dll", cairo_gobject_src_path, runtime_dest_path)
            else:
                copy(self, "cairo-static.lib", lib_src_path, lib_dest_path)
                copy(self, "cairo-gobject.lib", cairo_gobject_src_path, lib_dest_path)
                rename(self, os.path.join(lib_dest_path, "cairo-static.lib"), os.path.join(lib_dest_path, "cairo.lib"))
        else:
            autotools = Autotools(self, namespace="main")
            autotools.install()

        copy(self, "COPYING*", self.source_folder, os.path.join(self.package_folder, "licenses"))
        rm(self, "*.la", self.package_folder, recursive=True)
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "cairo-all-do-no-use")

        self.cpp_info.components["cairo_"].set_property("pkg_config_name", "cairo")
        self.cpp_info.components["cairo_"].libs = ["cairo"]
        self.cpp_info.components["cairo_"].includedirs.insert(0, os.path.join("include", "cairo"))
        self.cpp_info.components["cairo_"].requires = ["pixman::pixman", "libpng::libpng", "zlib::zlib"]

        if self.options.get_safe("with_freetype", True):
            self.cpp_info.components["cairo_"].requires.append("freetype::freetype")

        if self.settings.os == "Windows":
            self.cpp_info.components["cairo_"].system_libs.extend(["gdi32", "msimg32", "user32"])
            if not self.options.shared:
                self.cpp_info.components["cairo_"].defines.append("CAIRO_WIN32_STATIC_BUILD=1")
        else:
            if self.options.with_glib:
                self.cpp_info.components["cairo_"].requires.extend(["glib::gobject-2.0", "glib::glib-2.0"])
            if self.options.with_fontconfig:
                self.cpp_info.components["cairo_"].requires.append("fontconfig::fontconfig")

        if self.settings.os == "Linux":
            self.cpp_info.components["cairo_"].system_libs = ["pthread", "rt"]
            self.cpp_info.components["cairo_"].cflags = ["-pthread"]
            self.cpp_info.components["cairo_"].cxxflags = ["-pthread"]
            if self.options.with_xcb:
                self.cpp_info.components["cairo_"].requires.extend(["xorg::xcb-shm", "xorg::xcb"])
            if self.options.with_xlib_xrender:
                self.cpp_info.components["cairo_"].requires.extend(["xorg::xcb-render"])
            if self.options.with_xlib:
                self.cpp_info.components["cairo_"].requires.extend(["xorg::x11", "xorg::xext"])

        if is_apple_os(self):
            self.cpp_info.components["cairo_"].frameworks.append("CoreGraphics")

        if self.settings.os == "Windows":
            self.cpp_info.components["cairo-win32"].set_property("pkg_config_name", "cairo-win32")
            self.cpp_info.components["cairo-win32"].requires = ["cairo_", "pixman::pixman", "libpng::libpng"]

        if self.options.get_safe("with_glib", True):
            self.cpp_info.components["cairo-gobject"].set_property("pkg_config_name", "cairo-gobject")
            self.cpp_info.components["cairo-gobject"].libs = ["cairo-gobject"]
            self.cpp_info.components["cairo-gobject"].requires = ["cairo_", "glib::gobject-2.0", "glib::glib-2.0"]
        if self.settings.os != "Windows":
            if self.options.with_fontconfig:
                self.cpp_info.components["cairo-fc"].set_property("pkg_config_name", "cairo-fc")
                self.cpp_info.components["cairo-fc"].requires = ["cairo_", "fontconfig::fontconfig"]
            if self.options.get_safe("with_freetype", True):
                self.cpp_info.components["cairo-ft"].set_property("pkg_config_name", "cairo-ft")
                self.cpp_info.components["cairo-ft"].requires = ["cairo_", "freetype::freetype"]

            self.cpp_info.components["cairo-pdf"].set_property("pkg_config_name", "cairo-pdf")
            self.cpp_info.components["cairo-pdf"].requires = ["cairo_", "zlib::zlib"]

        if self.settings.os == "Linux":
            if self.options.with_xlib:
                self.cpp_info.components["cairo-xlib"].set_property("pkg_config_name", "cairo-xlib")
                self.cpp_info.components["cairo-xlib"].requires = ["cairo_", "xorg::x11", "xorg::xext"]

        if is_apple_os(self):
            self.cpp_info.components["cairo-quartz"].set_property("pkg_config_name", "cairo-quartz")
            self.cpp_info.components["cairo-quartz"].requires = ["cairo_"]
            self.cpp_info.components["cairo-quartz"].frameworks.extend(["CoreFoundation", "CoreGraphics", "ApplicationServices"])

            self.cpp_info.components["cairo-quartz-font"].set_property("pkg_config_name", "cairo-quartz-font")
            self.cpp_info.components["cairo-quartz-font"].requires = ["cairo_"]
