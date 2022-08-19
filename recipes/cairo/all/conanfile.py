import os
import shutil

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools import files, microsoft, scm
from conans import AutoToolsBuildEnvironment, VisualStudioBuildEnvironment
from conans import tools

required_conan_version = ">=1.50.0"


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

    exports_sources = "patches/*"
    generators = "pkg_config"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.with_fontconfig
        if microsoft.is_msvc(self):
            del self.options.with_freetype
            del self.options.with_glib
        if self.settings.os != "Linux":
            del self.options.with_xlib
            del self.options.with_xlib_xrender
            del self.options.with_xcb

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx
        if microsoft.is_msvc(self):
            if self.settings.build_type not in ["Debug", "Release"]:
                raise ConanInvalidConfiguration("MSVC build supports only Debug or Release build type")

    def requirements(self):
        if self.options.get_safe("with_freetype", True):
            self.requires("freetype/2.11.0")
        if self.options.get_safe("with_fontconfig", False):
            self.requires("fontconfig/2.13.93")
        if self.settings.os == "Linux":
            if self.options.with_xlib or self.options.with_xlib_xrender or self.options.with_xcb:
                self.requires("xorg/system")
        if self.options.get_safe("with_glib", True):
            self.requires("glib/2.70.0")
        self.requires("zlib/1.2.11")
        self.requires("pixman/0.40.0")
        self.requires("libpng/1.6.37")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        if not microsoft.is_msvc(self):
            self.build_requires("libtool/2.4.6")
            self.build_requires("pkgconf/1.7.4")
            self.build_requires("gtk-doc-stub/cci.20181216")

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            files.patch(self, **patch)
        if microsoft.is_msvc(self):
            self._build_msvc()
        else:
            self._build_configure()

    def _build_msvc(self):
        with tools.chdir(self._source_subfolder):
            # https://cairographics.org/end_to_end_build_for_win32/
            win32_common = os.path.join("build", "Makefile.win32.common")
            files.replace_in_file(self, win32_common, "-MD ", f"-{self.settings.compiler.runtime} ")
            files.replace_in_file(self, win32_common, "-MDd ", f"-{self.settings.compiler.runtime} ")
            files.replace_in_file(self, win32_common, "$(ZLIB_PATH)/lib/zlib1.lib",
                                                self.deps_cpp_info["zlib"].libs[0] + ".lib")
            files.replace_in_file(self, win32_common, "$(LIBPNG_PATH)/lib/libpng16.lib",
                                                self.deps_cpp_info["libpng"].libs[0] + ".lib")
            files.replace_in_file(self, win32_common, "$(FREETYPE_PATH)/lib/freetype.lib",
                                                self.deps_cpp_info["freetype"].libs[0] + ".lib")
            with tools.vcvars(self.settings):
                env_msvc = VisualStudioBuildEnvironment(self)
                env_msvc.flags.append("/FS")  # C1041 if multiple CL.EXE write to the same .PDB file, please use /FS
                with tools.environment_append(env_msvc.vars):
                    env_build = AutoToolsBuildEnvironment(self)
                    args=[
                        "-f", "Makefile.win32",
                        f"CFG={str(self.settings.build_type).lower()}",
                        "CAIRO_HAS_FC_FONT=0",
                        f"ZLIB_PATH={self.deps_cpp_info['zlib'].rootpath}",
                        f"LIBPNG_PATH={self.deps_cpp_info['libpng'].rootpath}",
                        f"PIXMAN_PATH={self.deps_cpp_info['pixman'].rootpath}",
                        f"FREETYPE_PATH={self.deps_cpp_info['freetype'].rootpath}",
                        f"GOBJECT_PATH={self.deps_cpp_info['glib'].rootpath}"
                    ]

                    env_build.make(args=args)
                    env_build.make(args=["-C", os.path.join("util", "cairo-gobject")] + args)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools

        def boolean(value):
            return "yes" if value else "no"

        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        configure_args = [
            f"--datarootdir={tools.unix_path(os.path.join(self.package_folder, 'res'))}",
            f"--enable-ft={boolean(self.options.with_freetype)}",
            f"--enable-gobject={boolean(self.options.with_glib)}",
            f"--enable-fc={boolean(self.options.get_safe('with_fontconfig'))}",
            f"--enable-xlib={boolean(self.options.get_safe('with_xlib'))}",
            f"--enable-xlib_xrender={boolean(self.options.get_safe('with_xlib_xrender'))}",
            f"--enable-xcb={boolean(self.options.get_safe('xcb'))}",
            f"--enable-shared={boolean(self.options.shared)}",
            f"--enable-static={boolean(not self.options.shared)}",
            "--disable-gtk-doc",
        ]
        if self.settings.compiler in ["gcc", "clang", "apple-clang"]:
            self._autotools.flags.append("-Wno-enum-conversion")

        with tools.run_environment(self):
            self._autotools.configure(args=configure_args, configure_dir=self._source_subfolder)
        return self._autotools

    def _build_configure(self):
        with tools.chdir(self._source_subfolder):
            # disable build of test suite
            files.replace_in_file(self, os.path.join("test", "Makefile.am"), "noinst_PROGRAMS = cairo-test-suite$(EXEEXT)",
                                  "")
            if self.options.with_freetype:
                files.replace_in_file(self, os.path.join(self.source_folder, self._source_subfolder, "src", "cairo-ft-font.c"),
                                      "#if HAVE_UNISTD_H", "#ifdef HAVE_UNISTD_H")

            tools.touch(os.path.join("boilerplate", "Makefile.am.features"))
            tools.touch(os.path.join("src", "Makefile.am.features"))
            tools.touch("ChangeLog")

            with tools.environment_append({"GTKDOCIZE": "echo"}):
                self.run(
                    f"{tools.get_env('AUTORECONF')} -fiv",
                    run_environment=True,
                    win_bash=tools.os_info.is_windows,
                )
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        if microsoft.is_msvc(self):
            src = os.path.join(self._source_subfolder, "src")
            cairo_gobject = os.path.join(self._source_subfolder, "util", "cairo-gobject")
            inc = os.path.join("include", "cairo")
            self.copy(pattern="cairo-version.h", dst=inc, src=(src if scm.Version(self.version) >= "1.17.4" else self._source_subfolder))
            self.copy(pattern="cairo-features.h", dst=inc, src=src)
            self.copy(pattern="cairo.h", dst=inc, src=src)
            self.copy(pattern="cairo-deprecated.h", dst=inc, src=src)
            self.copy(pattern="cairo-win32.h", dst=inc, src=src)
            self.copy(pattern="cairo-script.h", dst=inc, src=src)
            self.copy(pattern="cairo-ft.h", dst=inc, src=src)
            self.copy(pattern="cairo-ps.h", dst=inc, src=src)
            self.copy(pattern="cairo-pdf.h", dst=inc, src=src)
            self.copy(pattern="cairo-svg.h", dst=inc, src=src)
            self.copy(pattern="cairo-gobject.h", dst=inc, src=cairo_gobject)
            if self.options.shared:
                self.copy(pattern="*cairo.lib", dst="lib", src=src, keep_path=False)
                self.copy(pattern="*cairo.dll", dst="bin", src=src, keep_path=False)
                self.copy(pattern="*cairo-gobject.lib", dst="lib", src=cairo_gobject, keep_path=False)
                self.copy(pattern="*cairo-gobject.dll", dst="bin", src=cairo_gobject, keep_path=False)
            else:
                self.copy(pattern="*cairo-static.lib", dst="lib", src=src, keep_path=False)
                self.copy(pattern="*cairo-gobject.lib", dst="lib", src=cairo_gobject, keep_path=False)
                shutil.move(os.path.join(self.package_folder, "lib", "cairo-static.lib"),
                            os.path.join(self.package_folder, "lib", "cairo.lib"))
        else:
            autotools = self._configure_autotools()
            autotools.install()
        tools.remove_files_by_mask(self.package_folder, "*.la")

        self.copy("COPYING*", src=self._source_subfolder, dst="licenses", keep_path=False)
        files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

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

        if tools.is_apple_os(self.settings.os):
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

        if tools.is_apple_os(self.settings.os):
            self.cpp_info.components["cairo-quartz"].set_property("pkg_config_name", "cairo-quartz")
            self.cpp_info.components["cairo-quartz"].requires = ["cairo_"]
            self.cpp_info.components["cairo-quartz"].frameworks.extend(["CoreFoundation", "CoreGraphics", "ApplicationServices"])

            self.cpp_info.components["cairo-quartz-font"].set_property("pkg_config_name", "cairo-quartz-font")
            self.cpp_info.components["cairo-quartz-font"].requires = ["cairo_"]
            
    def package_id(self):
        if self.options.get_safe("with_glib") and not self.options["glib"].shared:
            self.info.requires["glib"].full_package_mode()
