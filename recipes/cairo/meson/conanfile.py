from conans import ConanFile, tools, Meson
from conans.errors import ConanInvalidConfiguration
import glob
import os
import shutil


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
        "with_zlib": [True, False],
        "with_png": [True, False],
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
        "with_zlib": True,
        "with_png": True,
    }

    exports_sources = "patches/*"
    generators = "pkg_config"

    _meson = None

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
        if self.settings.os != "Linux":
            del self.options.with_xlib
            del self.options.with_xlib_xrender
            del self.options.with_xcb

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def requirements(self):
        self.requires('expat/2.4.1')  # cairo-xml
        self.requires("pixman/0.40.0")
        if self.options.get_safe("with_zlib", True):
            self.requires("zlib/1.2.11")
        if self.options.get_safe("with_freetype", True):
            self.requires("freetype/2.11.0")
        if self.options.get_safe("with_fontconfig", True):
            self.requires("fontconfig/2.13.93")
        if self.options.get_safe("with_png", True):
            self.requires('libpng/1.6.37')
        if self.options.get_safe("with_glib", True):
            self.requires("glib/2.70.0")
        if self.settings.os == "Linux":
            if self.options.with_xlib or self.options.with_xlib_xrender or self.options.with_xcb:
                self.requires("xorg/system")

    def build_requirements(self):
        self.build_requires("meson/0.59.1")
        self.build_requires("pkgconf/1.7.4")

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_meson(self):
        yes_no = lambda v: "enabled" if v else "disabled"
        meson = Meson(self)
        defs = dict()
        defs["tests"] = "disabled"
        defs["zlib"] = yes_no(self.options.get_safe("with_zlib", True))
        defs["png"] = yes_no(self.options.get_safe("with_png", True))
        defs["freetype"] = yes_no(self.options.get_safe("with_freetype", True))
        defs["fontconfig"] = yes_no(self.options.get_safe("with_fontconfig", True))
        if self.settings.os == "Linux":
            defs["xcb"] = yes_no(self.options.get_safe("with_xcb", True))
            defs["xlib"] = yes_no(self.options.get_safe("with_xlib", True))
        else:
            defs['xcb'] = "disabled"
            defs["xlib"] = 'disabled'

        # future options to add, see meson_options.txt.
        # for now, disabling explicitly, to avoid non-reproducible auto-detection of system libs
        defs["cogl"] = "disabled"  # https://gitlab.gnome.org/GNOME/cogl
        defs["directfb"] = "disabled"
        defs["gl-backend"] = "disabled"  # 'gl', 'glesv2', 'glesv3', opengl/system?
        defs["glesv2"] = "disabled"
        defs["glesv3"] = "disabled"
        defs["drm"] = "disabled"
        defs["openvg"] = "disabled"  # https://www.khronos.org/openvg/
        defs["qt"] = "disabled"  # qt/6.2.0 - potential cyclic dependency via GLib?
        defs["tee"] = "disabled"  # no idea what is tee
        defs["gtk2-utils"] = "disabled"
        defs["spectre"] = "disabled"  # https://www.freedesktop.org/wiki/Software/libspectre/

        if not self.options.shared and self.settings.compiler == "Visual Studio":
            meson.options["c_args"] = " -DCAIRO_WIN32_STATIC_BUILD"
            meson.options["cpp_args"] = " -DCAIRO_WIN32_STATIC_BUILD"
        meson.configure(
            source_folder=self._source_subfolder,
            args=["--wrap-mode=nofallback"],
            build_folder=self._build_subfolder,
            defs=defs,
        )
        return meson

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        # Dependency freetype2 found: NO found 2.11.0 but need: '>= 9.7.3'
        if self.options.get_safe("with_freetype", True):
            tools.replace_in_file("freetype2.pc",
                                  "Version: %s" % self.deps_cpp_info["freetype"].version,
                                  "Version: 9.7.3")

        meson = self._configure_meson()
        meson.build()

    def _fix_library_names(self):
        if self.settings.compiler == "Visual Studio":
            with tools.chdir(os.path.join(self.package_folder, "lib")):
                for filename_old in glob.glob("*.a"):
                    filename_new = filename_old[3:-2] + ".lib"
                    self.output.info("rename %s into %s" % (filename_old, filename_new))
                    shutil.move(filename_old, filename_new)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("COPYING*", src=self._source_subfolder, dst="licenses", keep_path=False)
        meson = self._configure_meson()
        meson.install()
        self._fix_library_names()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.pdb")

    def package_info(self):
        self.cpp_info.components["cairo_"].names["pkg_config"] = "cairo"
        self.cpp_info.components["cairo_"].libs = ["cairo"]
        self.cpp_info.components["cairo_"].includedirs.insert(0, os.path.join("include", "cairo"))
        self.cpp_info.components["cairo_"].requires = ["pixman::pixman", "libpng::libpng", "zlib::zlib"]
        if self.options.get_safe("with_freetype", True):
            self.cpp_info.components["cairo_"].requires.append("freetype::freetype")

        if self.settings.os == "Windows":
            self.cpp_info.components["cairo_"].system_libs.extend(["gdi32", "msimg32", "user32"])
            if not self.options.shared:
                self.cpp_info.components["cairo_"].defines.append("CAIRO_WIN32_STATIC_BUILD=1")

        if self.options.get_safe("with_glib", True):
            self.cpp_info.components["cairo_"].requires.extend(["glib::gobject-2.0", "glib::glib-2.0"])
        if self.options.get_safe("with_fontconfig", True):
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

        self.cpp_info.components["cairo-xml"].names["pkg_config"] = "cairo-xml"
        self.cpp_info.components["cairo-xml"].requires = ["cairo_", "expat::expat"]

        if self.settings.os == "Windows":
            self.cpp_info.components["cairo-win32"].names["pkg_config"] = "cairo-win32"
            self.cpp_info.components["cairo-win32"].requires = ["cairo_", "pixman::pixman", "libpng::libpng"]

            self.cpp_info.components["cairo-win32-font"].names["pkg_config"] = "cairo-win32-font"
            self.cpp_info.components["cairo-win32-font"].requires = ["cairo_"]

        if self.options.get_safe("with_glib", True):
            self.cpp_info.components["cairo-gobject"].names["pkg_config"] = "cairo-gobject"
            self.cpp_info.components["cairo-gobject"].libs = ["cairo-gobject"]
            self.cpp_info.components["cairo-gobject"].requires = ["cairo_", "glib::gobject-2.0", "glib::glib-2.0"]
        if self.options.get_safe("with_fontconfig", True):
            self.cpp_info.components["cairo-fc"].names["pkg_config"] = "cairo-fc"
            self.cpp_info.components["cairo-fc"].requires = ["cairo_", "fontconfig::fontconfig"]
        if self.options.get_safe("with_freetype", True):
            self.cpp_info.components["cairo-ft"].names["pkg_config"] = "cairo-ft"
            self.cpp_info.components["cairo-ft"].requires = ["cairo_", "freetype::freetype"]
        if self.options.get_safe("with_zlib", True):
            self.cpp_info.components["cairo-pdf"].names["pkg_config"] = "cairo-pdf"
            self.cpp_info.components["cairo-pdf"].requires = ["cairo_", "zlib::zlib"]
        if self.options.get_safe("with_png", True):
            self.cpp_info.components["cairo-png"].names["pkg_config"] = "cairo-png"
            self.cpp_info.components["cairo-png"].requires = ["cairo_", "libpng::libpng"]

        self.cpp_info.components["cairo-ps"].names["pkg_config"] = "cairo-ps"
        self.cpp_info.components["cairo-ps"].requires = ["cairo_"]

        self.cpp_info.components["cairo-script"].names["pkg_config"] = "cairo-script"
        self.cpp_info.components["cairo-script"].requires = ["cairo_"]

        self.cpp_info.components["cairo-svg"].names["pkg_config"] = "cairo-svg"
        self.cpp_info.components["cairo-svg"].requires = ["cairo_"]

        if self.settings.os == "Linux":
            if self.options.get_safe("with_xlib", True):
                self.cpp_info.components["cairo-xlib"].names["pkg_config"] = "cairo-xlib"
                self.cpp_info.components["cairo-xlib"].requires = ["cairo_", "xorg::x11", "xorg::xext"]

        if tools.is_apple_os(self.settings.os):
            self.cpp_info.components["cairo-quartz"].names["pkg_config"] = "cairo-quartz"
            self.cpp_info.components["cairo-quartz"].requires = ["cairo_"]
            self.cpp_info.components["cairo-quartz"].frameworks.extend(["CoreFoundation", "CoreGraphics"])
            self.cpp_info.components["cairo-quartz-font"].names["pkg_config"] = "cairo-quartz-font"
            self.cpp_info.components["cairo-quartz-font"].requires = ["cairo_"]
