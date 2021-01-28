from conans import ConanFile, AutoToolsBuildEnvironment, tools, VisualStudioBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import os
import shutil


class CairoConan(ConanFile):
    name = "cairo"
    description = "Cairo is a 2D graphics library with support for multiple output devices"
    topics = ("conan", "cairo", "graphics")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://cairographics.org/"
    license = ("LGPL-2.1-only", "MPL-1.1")
    exports_sources = ["patches/*"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
        "fPIC": [True, False],
        "with_freetype": [True, False],
        "with_fontconfig": [True, False],
        "with_xlib": [True, False],
        "with_xlib_xrender": [True, False],
        "with_xcb": [True, False],
        "with_glib": [True, False]}
    default_options = {'shared': False,
        'fPIC': True,
        "with_freetype": True,
        "with_fontconfig": True,
        "with_xlib": True,
        "with_xlib_xrender": False,
        "with_xcb": True,
        "with_glib": True}
    generators = "pkg_config"

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    _env_build = None

    def config_options(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os == 'Windows':
            del self.options.fPIC
            del self.options.with_fontconfig
        if self.settings.os != 'Linux':
            del self.options.with_xlib
            del self.options.with_xlib_xrender
            del self.options.with_xcb

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx
        if self._is_msvc:
            if self.settings.build_type not in ['Debug', 'Release']:
                raise ConanInvalidConfiguration("MSVC build supports only Debug or Release build type")

    def requirements(self):
        if self.options.with_freetype:
            self.requires("freetype/2.10.4")
        if self.options.get_safe("with_fontconfig", False):
            self.requires("fontconfig/2.13.92")
        if self.settings.os == 'Linux':
            if self.options.with_xlib or self.options.with_xlib_xrender or self.options.with_xcb:
                self.requires("xorg/system")
        if self.options.with_glib:
            self.requires("glib/2.67.0")
        self.requires("zlib/1.2.11")
        self.requires("pixman/0.40.0")
        self.requires("libpng/1.6.37")

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires('msys2/20200517')
        if not self._is_msvc:
            self.build_requires("libtool/2.4.6")
            self.build_requires("pkgconf/1.7.3")

    @property
    def _is_msvc(self):
        return self.settings.compiler == 'Visual Studio'

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename('cairo-%s' % self.version, self._source_subfolder)

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        if self._is_msvc:
            self._build_msvc()
        else:
            self._build_configure()

    def _build_msvc(self):
        with tools.chdir(self._source_subfolder):
            # https://cairographics.org/end_to_end_build_for_win32/
            win32_common = os.path.join('build', 'Makefile.win32.common')
            tools.replace_in_file(win32_common, '-MD ', '-%s ' % self.settings.compiler.runtime)
            tools.replace_in_file(win32_common, '-MDd ', '-%s ' % self.settings.compiler.runtime)
            tools.replace_in_file(win32_common, '$(ZLIB_PATH)/lib/zlib1.lib',
                                                self.deps_cpp_info['zlib'].libs[0] + '.lib')
            tools.replace_in_file(win32_common, '$(LIBPNG_PATH)/lib/libpng16.lib',
                                                self.deps_cpp_info['libpng'].libs[0] + '.lib')
            tools.replace_in_file(win32_common, '$(FREETYPE_PATH)/lib/freetype.lib',
                                                self.deps_cpp_info['freetype'].libs[0] + '.lib')
            with tools.vcvars(self.settings):
                env_msvc = VisualStudioBuildEnvironment(self)
                env_msvc.flags.append('/FS')  # C1041 if multiple CL.EXE write to the same .PDB file, please use /FS
                with tools.environment_append(env_msvc.vars):
                    env_build = AutoToolsBuildEnvironment(self)
                    args=[
                        "-f", "Makefile.win32",
                        "CFG={}".format(str(self.settings.build_type).lower()),
                        "CAIRO_HAS_FC_FONT=0",
                        "ZLIB_PATH={}".format(self.deps_cpp_info["zlib"].rootpath),
                        "LIBPNG_PATH={}".format(self.deps_cpp_info["libpng"].rootpath),
                        "PIXMAN_PATH={}".format(self.deps_cpp_info['pixman'].rootpath),
                        "FREETYPE_PATH={}".format(self.deps_cpp_info['freetype'].rootpath),
                        "GOBJECT_PATH={}".format(self.deps_cpp_info['glib'].rootpath)
                    ]

                    env_build.make(args=args)
                    env_build.make(args=['-C', os.path.join('util', 'cairo-gobject')] + args)

    def _get_env_build(self):
        if self._env_build:
            return self._env_build

        self._env_build = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        yes_no = lambda v: "yes" if v else "no"
        configure_args = [
            "--datarootdir={}".format(tools.unix_path(os.path.join(self.package_folder, "res"))),
            "--enable-ft={}".format(yes_no(self.options.with_freetype)),
            "--enable-gobject={}".format(yes_no(self.options.with_glib)),
            "--enable-fc={}".format(yes_no(self.options.get_safe("with_fontconfig"))),
            "--enable-xlib={}".format(yes_no(self.options.get_safe("with_xlib"))),
            "--enable-xlib_xrender={}".format(yes_no(self.options.get_safe("with_xlib_xrender"))),
            "--enable-xcb={}".format(yes_no(self.options.get_safe("xcb"))),
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        if self.settings.compiler in ["gcc", "clang", "apple-clang"]:
            self._env_build.flags.append("-Wno-enum-conversion")

        self._env_build.configure(args=configure_args)
        return self._env_build

    def _build_configure(self):
        with tools.chdir(self._source_subfolder):
            # disable build of test suite
            tools.replace_in_file(os.path.join('test', 'Makefile.am'), 'noinst_PROGRAMS = cairo-test-suite$(EXEEXT)',
                                  '')
            if self.options.with_freetype:
                tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "src", "cairo-ft-font.c"),
                                      '#if HAVE_UNISTD_H', '#ifdef HAVE_UNISTD_H')

            with tools.environment_append({"NOCONFIGURE": "1"}):
                self.run("./autogen.sh", win_bash=tools.os_info.is_windows, run_environment=True)
            env_build = self._get_env_build()
            env_build.make()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        if self._is_msvc:
            src = os.path.join(self._source_subfolder, 'src')
            cairo_gobject = os.path.join(self._source_subfolder, 'util', 'cairo-gobject')
            inc = os.path.join('include', 'cairo')
            self.copy(pattern="cairo-version.h", dst=inc, src=(src if tools.Version(self.version) >= "1.17.4" else self._source_subfolder))
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
                shutil.move(os.path.join(self.package_folder, 'lib', "cairo-static.lib"),
                            os.path.join(self.package_folder, 'lib', "cairo.lib"))
        else:
            with tools.chdir(self._source_subfolder):
                env_build = self._get_env_build()
                env_build.install()
        tools.remove_files_by_mask(self.package_folder, "*.la")

        self.copy("COPYING*", src=self._source_subfolder, dst="licenses", keep_path=False)
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))


    def package_info(self):
        self.cpp_info.components["cairo_"].names["pkg_config"] = "cairo"
        self.cpp_info.components["cairo_"].libs = ["cairo"]
        self.cpp_info.components["cairo_"].includedirs.insert(0, os.path.join('include', 'cairo'))
        self.cpp_info.components["cairo_"].requires = ["pixman::pixman", "libpng::libpng", "zlib::zlib"]
        if self.options.with_freetype:
            self.cpp_info.components["cairo_"].requires.append("freetype::freetype")

        if self.settings.os == "Windows":
            self.cpp_info.components["cairo_"].system_libs.extend(['gdi32','msimg32','user32'])
            if not self.options.shared:
                self.cpp_info.components["cairo_"].defines.append('CAIRO_WIN32_STATIC_BUILD=1')
        else:
            if self.options.with_glib:
                self.cpp_info.components["cairo_"].requires.extend(["glib::gobject-2.0", "glib::glib-2.0"])
            if self.options.with_fontconfig:
                self.cpp_info.components["cairo_"].requires.append("fontconfig::fontconfig")
        if self.settings.os == "Linux":
            self.cpp_info.components["cairo_"].system_libs = ["pthread"]
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
            self.cpp_info.components["cairo-win32"].names["pkg_config"] = "cairo-win32"
            self.cpp_info.components["cairo-win32"].requires = ["cairo_", "pixman::pixman", "libpng::libpng"]

        if self.options.with_glib:
            self.cpp_info.components["cairo-gobject"].names["pkg_config"] = "cairo-gobject"
            self.cpp_info.components["cairo-gobject"].libs = ["cairo-gobject"]
            self.cpp_info.components["cairo-gobject"].requires = ["cairo_", "glib::gobject-2.0", "glib::glib-2.0"]
        if self.settings.os != "Windows":
            if self.options.with_fontconfig:
                self.cpp_info.components["cairo-fc"].names["pkg_config"] = "cairo-fc"
                self.cpp_info.components["cairo-fc"].requires = ["cairo_", "fontconfig::fontconfig"]
            if self.options.with_freetype:
                self.cpp_info.components["cairo-ft"].names["pkg_config"] = "cairo-ft"
                self.cpp_info.components["cairo-ft"].requires = ["cairo_", "freetype::freetype"]
            self.cpp_info.components["cairo-pdf"].names["pkg_config"] = "cairo-pdf"
            self.cpp_info.components["cairo-pdf"].requires = ["cairo_", "zlib::zlib"]

        if self.settings.os == "Linux":
            if self.options.with_xlib:
                self.cpp_info.components["cairo-xlib"].names["pkg_config"] = "cairo-xlib"
                self.cpp_info.components["cairo-xlib"].requires = ["cairo_", "xorg::x11", "xorg::xext"]

        if tools.is_apple_os(self.settings.os):
            self.cpp_info.components["cairo-quartz"].names["pkg_config"] = "cairo-quartz"
            self.cpp_info.components["cairo-quartz"].requires = ["cairo_"]
            self.cpp_info.components["cairo-quartz-font"].names["pkg_config"] = "cairo-quartz-font"
            self.cpp_info.components["cairo-quartz-font"].requires = ["cairo_"]
