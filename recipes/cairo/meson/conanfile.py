from conans import ConanFile, tools, Meson, VisualStudioBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import contextlib
import glob
import os

required_conan_version = ">=1.38.0"

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
        "with_lzo": [True, False],
        "with_zlib": [True, False],
        "with_png": [True, False],
        "with_opengl": [False, "desktop", "gles2", "gles3"],
        "with_symbol_lookup": [True, False],
        "tee": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_freetype": True,
        "with_fontconfig": True,
        "with_xlib": True,
        "with_xlib_xrender": True,
        "with_xcb": True,
        "with_glib": True,
        "with_lzo": True,
        "with_zlib": True,
        "with_png": True,
        "with_opengl": "desktop",
        "with_symbol_lookup": False,
        "tee": True,
    }

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

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.with_xlib
            del self.options.with_xlib_xrender
            del self.options.with_xcb
            del self.options.with_symbol_lookup
        if self.settings.os in ["Macos", "Windows"]:
            del self.options.with_opengl

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx
        if self.options.with_glib and self.options.shared:
            self.options["glib"].shared = True

    def requirements(self):
        self.requires("pixman/0.40.0")
        if self.options.with_zlib and self.options.with_png:
            self.requires("expat/2.4.8")
        if self.options.with_lzo:
            self.requires("lzo/2.10")
        if self.options.with_zlib:
            self.requires("zlib/1.2.12")
        if self.options.with_freetype:
            self.requires("freetype/2.12.1")
        if self.options.with_fontconfig:
            self.requires("fontconfig/2.13.93")
        if self.options.with_png:
            self.requires("libpng/1.6.37")
        if self.options.with_glib:
            self.requires("glib/2.73.0")
        if self.settings.os == "Linux":
            if self.options.with_xlib or self.options.with_xlib_xrender or self.options.with_xcb:
                self.requires("xorg/system")
        if self.options.get_safe("with_opengl") == "desktop":
            self.requires("opengl/system")
            if self.settings.os == "Windows":
                self.requires("glext/cci.20210420")
                self.requires("wglext/cci.20200813")
                self.requires("khrplatform/cci.20200529")
        if self.options.get_safe("with_opengl") and self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("egl/system")

    def build_requirements(self):
        self.build_requires("meson/0.62.1")
        self.build_requires("pkgconf/1.7.4")

    def validate(self):
        if self.options.get_safe("with_xlib_xrender") and not self.options.get_safe("with_xlib"):
            raise ConanInvalidConfiguration("'with_xlib_xrender' option requires 'with_xlib' option to be enabled as well!")
        if self.options.with_glib and not self.options["glib"].shared and self.options.shared:
            raise ConanInvalidConfiguration(
                "Linking a shared library against static glib can cause unexpected behaviour."
            )

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["msvc", "Visual Studio"]

    @contextlib.contextmanager
    def _build_context(self):
        if self._is_msvc:
            env_build = VisualStudioBuildEnvironment(self)
            if not self.options.shared:
                env_build.flags.append("-DCAIRO_WIN32_STATIC_BUILD")
                env_build.cxx_flags.append("-DCAIRO_WIN32_STATIC_BUILD")
            with tools.environment_append(env_build.vars):
                yield
        else:
            yield

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_meson(self):
        yes_no = lambda v: "enabled" if v else "disabled"
        meson = Meson(self)

        defs = dict()
        defs["tests"] = "disabled"
        defs["zlib"] = yes_no(self.options.with_zlib)
        defs["png"] = yes_no(self.options.with_png)
        defs["freetype"] = yes_no(self.options.with_freetype)
        defs["fontconfig"] = yes_no(self.options.with_fontconfig)
        if self.settings.os == "Linux":
            defs["xcb"] = yes_no(self.options.get_safe("with_xcb"))
            defs["xlib"] = yes_no(self.options.get_safe("with_xlib"))
            defs["xlib-xrender"] = yes_no(self.options.get_safe("with_xlib_xrender"))
        else:
            defs["xcb"] = "disabled"
            defs["xlib"] = "disabled"
        if self.options.get_safe("with_opengl") == "desktop":
            defs["gl-backend"] = "gl"
        elif self.options.get_safe("with_opengl") == "gles2":
            defs["gl-backend"] = "glesv2"
        elif self.options.get_safe("with_opengl") == "gles3":
            defs["gl-backend"] = "glesv3"
        else:
            defs["gl-backend"] = "disabled"
        defs["glesv2"] = yes_no(self.options.get_safe("with_opengl") == "gles2")
        defs["glesv3"] = yes_no(self.options.get_safe("with_opengl") == "gles3")
        defs["tee"] = yes_no(self.options.tee)
        defs["symbol-lookup"] = yes_no(self.options.get_safe("with_symbol_lookup"))

        # future options to add, see meson_options.txt.
        # for now, disabling explicitly, to avoid non-reproducible auto-detection of system libs
        defs["cogl"] = "disabled"  # https://gitlab.gnome.org/GNOME/cogl
        defs["directfb"] = "disabled"
        defs["drm"] = "disabled" # not yet compilable in cairo 1.17.4
        defs["openvg"] = "disabled"  # https://www.khronos.org/openvg/
        defs["qt"] = "disabled" # not yet compilable in cairo 1.17.4
        defs["gtk2-utils"] = "disabled"
        defs["spectre"] = "disabled"  # https://www.freedesktop.org/wiki/Software/libspectre/

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
        if self.options.with_freetype:
            tools.replace_in_file("freetype2.pc",
                                  "Version: %s" % self.deps_cpp_info["freetype"].version,
                                  "Version: 9.7.3")
        with self._build_context():
            meson = self._configure_meson()
            meson.build()

    def _fix_library_names(self):
        if self._is_msvc:
            with tools.chdir(os.path.join(self.package_folder, "lib")):
                for filename_old in glob.glob("*.a"):
                    filename_new = filename_old[3:-2] + ".lib"
                    self.output.info("rename %s into %s" % (filename_old, filename_new))
                    tools.rename(filename_old, filename_new)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("COPYING*", src=self._source_subfolder, dst="licenses", keep_path=False)
        with self._build_context():
            meson = self._configure_meson()
            meson.install()
        self._fix_library_names()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.pdb")

    def package_info(self):
        self.cpp_info.components["cairo_"].libs = ["cairo"]
        self.cpp_info.components["cairo_"].includedirs.insert(0, os.path.join("include", "cairo"))
        if self.settings.os == "Linux":
            self.cpp_info.components["cairo_"].system_libs.extend(["m", "dl", "pthread"])
            if self.options.get_safe("with_symbol_lookup"):
                self.cpp_info.components["cairo_"].system_libs.append("bfd")
            self.cpp_info.components["cairo_"].cflags = ["-pthread"]
            self.cpp_info.components["cairo_"].cxxflags = ["-pthread"]
        if self.options.with_lzo:
            self.cpp_info.components["cairo_"].requires.append("lzo::lzo")
        if self.options.with_zlib:
            self.cpp_info.components["cairo_"].requires.append("zlib::zlib")
        if self.options.with_png:
            self.cpp_info.components["cairo_"].requires.append("libpng::libpng")
        if self.options.with_fontconfig:
            self.cpp_info.components["cairo_"].requires.append("fontconfig::fontconfig")
        if self.options.with_freetype:
            self.cpp_info.components["cairo_"].requires.append("freetype::freetype")
        if self.options.get_safe("with_xlib"):
            self.cpp_info.components["cairo_"].requires.extend(["xorg::x11", "xorg::xext"])
        if self.options.get_safe("with_xlib_xrender"):
            self.cpp_info.components["cairo_"].requires.append("xorg::xrender")
        if self.options.get_safe("with_xcb"):
            self.cpp_info.components["cairo_"].requires.extend(["xorg::xcb", "xorg::xcb-render", "xorg::xcb-shm"])
        if self.options.get_safe("with_xlib") and self.options.get_safe("with_xcb"):
            self.cpp_info.components["cairo_"].requires.append("xorg::x11-xcb")
        if tools.is_apple_os(self.settings.os):
            self.cpp_info.components["cairo_"].frameworks.append("CoreGraphics")
        if self.settings.os == "Windows":
            self.cpp_info.components["cairo_"].system_libs.extend(["gdi32", "msimg32", "user32"])
            if not self.options.shared:
                self.cpp_info.components["cairo_"].defines.append("CAIRO_WIN32_STATIC_BUILD=1")
        if self.options.get_safe("with_opengl") == "desktop":
            self.cpp_info.components["cairo_"].requires.append("opengl::opengl")
            if self.settings.os == "Windows":
                self.cpp_info.components["cairo_"].requires.extend(["glext::glext", "wglext::wglext", "khrplatform::khrplatform"])
        if self.options.get_safe("with_opengl") and self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["cairo_"].requires.append("egl::egl")
        if self.options.get_safe("with_opengl") == "gles2" or self.options.get_safe("with_opengl") == "gles3":
            self.cpp_info.components["cairo_"].system_libs.append("GLESv2")
        self.cpp_info.components["cairo_"].requires.append("pixman::pixman")

        # built-features
        if self.options.with_png:
            self.cpp_info.components["cairo-png"].names["pkg_config"] = "cairo-png"
            self.cpp_info.components["cairo-png"].requires = ["cairo_", "libpng::libpng"]

        if self.options.with_png:
            self.cpp_info.components["cairo-svg"].names["pkg_config"] = "cairo-svg"
            self.cpp_info.components["cairo-svg"].requires = ["cairo_", "libpng::libpng"]

        if self.options.with_fontconfig:
            self.cpp_info.components["cairo-fc"].names["pkg_config"] = "cairo-fc"
            self.cpp_info.components["cairo-fc"].requires = ["cairo_", "fontconfig::fontconfig"]

        if self.options.with_freetype:
            self.cpp_info.components["cairo-ft"].names["pkg_config"] = "cairo-ft"
            self.cpp_info.components["cairo-ft"].requires = ["cairo_", "freetype::freetype"]

        if self.options.get_safe("with_xlib"):
            self.cpp_info.components["cairo-xlib"].names["pkg_config"] = "cairo-xlib"
            self.cpp_info.components["cairo-xlib"].requires = ["cairo_", "xorg::x11", "xorg::xext"]

        if self.options.get_safe("with_xlib_xrender"):
            self.cpp_info.components["cairo-xlib-xrender"].names["pkg_config"] = "cairo-xlib-xrender"
            self.cpp_info.components["cairo-xlib-xrender"].requires = ["cairo_", "xorg::xrender"]

        if self.options.get_safe("with_xcb"):
            self.cpp_info.components["cairo-xcb"].names["pkg_config"] = "cairo-xcb"
            self.cpp_info.components["cairo-xcb"].requires = ["cairo_", "xorg::xcb", "xorg::xcb-render"]

        if self.options.get_safe("with_xlib") and self.options.get_safe("with_xcb"):
            self.cpp_info.components["cairo-xlib-xcb"].names["pkg_config"] = "cairo-xlib-xcb"
            self.cpp_info.components["cairo-xlib-xcb"].requires = ["cairo_", "xorg::x11-xcb"]

        if self.options.get_safe("with_xcb"):
            self.cpp_info.components["cairo-xcb-shm"].names["pkg_config"] = "cairo-xcb-shm"
            self.cpp_info.components["cairo-xcb-shm"].requires = ["cairo_", "xorg::xcb-shm"]

        if tools.is_apple_os(self.settings.os):
            self.cpp_info.components["cairo-quartz"].names["pkg_config"] = "cairo-quartz"
            self.cpp_info.components["cairo-quartz"].requires = ["cairo_"]

            self.cpp_info.components["cairo-quartz-image"].names["pkg_config"] = "cairo-quartz-image"
            self.cpp_info.components["cairo-quartz-image"].requires = ["cairo_"]

            self.cpp_info.components["cairo-quartz-font"].names["pkg_config"] = "cairo-quartz-font"
            self.cpp_info.components["cairo-quartz-font"].requires = ["cairo_"]

        if self.settings.os == "Windows":
            self.cpp_info.components["cairo-win32"].names["pkg_config"] = "cairo-win32"
            self.cpp_info.components["cairo-win32"].requires = ["cairo_"]

            self.cpp_info.components["cairo-win32-font"].names["pkg_config"] = "cairo-win32-font"
            self.cpp_info.components["cairo-win32-font"].requires = ["cairo_"]

        if self.options.get_safe("with_opengl") == "desktop":
            self.cpp_info.components["cairo-gl"].names["pkg_config"] = "cairo-gl"
            self.cpp_info.components["cairo-gl"].requires = ["cairo_", "opengl::opengl"]

            if self.settings.os == "Linux":
                self.cpp_info.components["cairo-glx"].names["pkg_config"] = "cairo-glx"
                self.cpp_info.components["cairo-glx"].requires = ["cairo_", "opengl::opengl"]

            if self.settings.os == "Windows":
                self.cpp_info.components["cairo-wgl"].names["pkg_config"] = "cairo-wgl"
                self.cpp_info.components["cairo-wgl"].requires = ["cairo_", "glext::glext", "wglext::wglext"]

        if self.options.get_safe("with_opengl") == "gles2":
            self.cpp_info.components["cairo-glesv2"].names["pkg_config"] = "cairo-glesv2"
            self.cpp_info.components["cairo-glesv2"].requires = ["cairo_"]
            self.cpp_info.components["cairo-glesv2"].system_libs = ["GLESv2"]

        if self.options.get_safe("with_opengl") == "gles3":
            self.cpp_info.components["cairo-glesv3"].names["pkg_config"] = "cairo-glesv3"
            self.cpp_info.components["cairo-glesv3"].requires = ["cairo_"]
            self.cpp_info.components["cairo-glesv3"].system_libs = ["GLESv2"]

        if self.options.get_safe("with_opengl") and self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["cairo-egl"].names["pkg_config"] = "cairo-egl"
            self.cpp_info.components["cairo-egl"].requires = ["cairo_", "egl::egl"]

        if self.options.with_zlib:
            self.cpp_info.components["cairo-script"].names["pkg_config"] = "cairo-script"
            self.cpp_info.components["cairo-script"].requires = ["cairo_", "zlib::zlib"]

        if self.options.with_zlib:
            self.cpp_info.components["cairo-ps"].names["pkg_config"] = "cairo-ps"
            self.cpp_info.components["cairo-ps"].requires = ["cairo_", "zlib::zlib"]

        if self.options.with_zlib:
            self.cpp_info.components["cairo-pdf"].names["pkg_config"] = "cairo-pdf"
            self.cpp_info.components["cairo-pdf"].requires = ["cairo_", "zlib::zlib"]

        if self.options.with_zlib and self.options.with_png:
            self.cpp_info.components["cairo-xml"].names["pkg_config"] = "cairo-xml"
            self.cpp_info.components["cairo-xml"].requires = ["cairo_", "zlib::zlib"]

        if self.options.tee:
            self.cpp_info.components["cairo-tee"].names["pkg_config"] = "cairo-tee"
            self.cpp_info.components["cairo-tee"].requires = ["cairo_"]

        # util directory
        if self.options.with_glib:
            self.cpp_info.components["cairo-gobject"].names["pkg_config"] = "cairo-gobject"
            self.cpp_info.components["cairo-gobject"].libs = ["cairo-gobject"]
            self.cpp_info.components["cairo-gobject"].requires = ["cairo_", "glib::gobject-2.0", "glib::glib-2.0"]

        if self.options.with_zlib:
            self.cpp_info.components["cairo-script-interpreter"].libs = ["cairo-script-interpreter"]
            self.cpp_info.components["cairo-script-interpreter"].requires = ["cairo_"]

        # binary tools
        if self.options.with_zlib and self.options.with_png:
            self.cpp_info.components["cairo_util_"].requires.append("expat::expat") # trace-to-xml.c, xml-to-trace.c

    def package_id(self):
        self.info.requires["glib"].full_package_mode()
