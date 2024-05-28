import glob
import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rename, replace_in_file, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


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
        "tee": False,
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
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.with_xlib
            del self.options.with_xlib_xrender
            del self.options.with_xcb
            del self.options.with_symbol_lookup
        if Version(self.version) >= "1.17.8" or self.settings.os == "Windows" or is_apple_os(self):
            del self.options.with_opengl

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("pixman/0.43.4")
        if self.options.with_zlib and self.options.with_png:
            self.requires("expat/[>=2.6.2 <3]")
        if self.options.with_lzo:
            self.requires("lzo/2.10")
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_freetype:
            self.requires("freetype/2.13.2", transitive_headers=True, transitive_libs=True)
        if self.options.with_fontconfig:
            self.requires("fontconfig/2.15.0", transitive_headers=True, transitive_libs=True)
        if self.options.with_png:
            self.requires("libpng/[>=1.6 <2]")
        if self.options.with_glib:
            self.requires("glib/2.78.3")
        if self.settings.os in ["Linux", "FreeBSD"]:
            if self.options.with_xlib or self.options.with_xlib_xrender or self.options.with_xcb:
                self.requires("xorg/system", transitive_headers=True, transitive_libs=True)
        if self.options.get_safe("with_opengl") == "desktop":
            self.requires("opengl/system", transitive_headers=True, transitive_libs=True)
            if self.settings.os == "Windows":
                self.requires("glext/cci.20210420")
                self.requires("wglext/cci.20200813")
                self.requires("khrplatform/cci.20200529")
        if self.options.get_safe("with_opengl") and self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("egl/system", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.options.get_safe("with_xlib_xrender") and not self.options.get_safe("with_xlib"):
            raise ConanInvalidConfiguration("'with_xlib_xrender' option requires 'with_xlib' option to be enabled as well!")
        if self.options.with_glib:
            if self.dependencies["glib"].options.shared:
                if is_msvc_static_runtime(self):
                    raise ConanInvalidConfiguration(
                        "Linking shared glib with the MSVC static runtime is not supported"
                    )
            elif self.options.shared:
                raise ConanInvalidConfiguration(
                    "Linking a shared library against static glib can cause unexpected behaviour."
                )

    def build_requirements(self):
        self.tool_requires("meson/1.4.0")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.1.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        def is_enabled(value):
            return "enabled" if value else "disabled"

        env = VirtualBuildEnv(self)
        env.generate()

        pkg_deps = PkgConfigDeps(self)
        pkg_deps.generate()

        options = dict()
        options["tests"] = "disabled"
        options["zlib"] = is_enabled(self.options.with_zlib)
        options["png"] = is_enabled(self.options.with_png)
        options["freetype"] = is_enabled(self.options.with_freetype)
        options["fontconfig"] = is_enabled(self.options.with_fontconfig)
        if self.settings.os in ["Linux", "FreeBSD"]:
            options["xcb"] = is_enabled(self.options.with_xcb)
            options["xlib"] = is_enabled(self.options.with_xlib)
        else:
            options["xcb"] = "disabled"
            options["xlib"] = "disabled"
        if Version(self.version) < "1.17.8":
            if self.options.get_safe("with_opengl") == "desktop":
                options["gl-backend"] = "gl"
            elif self.options.get_safe("with_opengl") == "gles2":
                options["gl-backend"] = "glesv2"
            elif self.options.get_safe("with_opengl") == "gles3":
                options["gl-backend"] = "glesv3"
            else:
                options["gl-backend"] = "disabled"
            options["glesv2"] = is_enabled(self.options.get_safe("with_opengl") == "gles2")
            options["glesv3"] = is_enabled(self.options.get_safe("with_opengl") == "gles3")
        options["tee"] = is_enabled(self.options.tee)
        options["symbol-lookup"] = is_enabled(self.options.get_safe("with_symbol_lookup"))

        # future options to add, see meson_options.txt.
        # for now, disabling explicitly, to avoid non-reproducible auto-detection of system libs

        version = Version(self.version)
        if version < "1.17.6":
            options["cogl"] = "disabled"  # https://gitlab.gnome.org/GNOME/cogl
            options["directfb"] = "disabled"
            options["drm"] = "disabled"  # not yet compilable in cairo 1.17.4
            options["openvg"] = "disabled"  # https://www.khronos.org/openvg/
            options["qt"] = "disabled"  # not yet compilable in cairo 1.17.4
            if self.settings.os in ["Linux", "FreeBSD"]:
                options["xlib-xrender"] = is_enabled(self.options.with_xlib_xrender)

        options["gtk2-utils"] = "disabled"
        options["spectre"] = "disabled"  # https://www.freedesktop.org/wiki/Software/libspectre/

        meson = MesonToolchain(self)
        meson.project_options.update(options)

        if cross_building(self):
            meson.properties["ipc_rmid_deferred_release"] = self.settings.os == "Linux"

        if is_apple_os(self) and Version(self.version) < "1.17.6":
            # This was fixed in the meson build from 1.17.6
            meson.c_link_args += ["-framework", "ApplicationServices", "-framework", "CoreFoundation"]

        if not self.options.shared:
            meson.c_args.append("-DCAIRO_WIN32_STATIC_BUILD")

        meson.generate()

    def build(self):
        apply_conandata_patches(self)

        # Dependency freetype2 found: NO found 2.11.0 but need: '>= 9.7.3'
        if self.options.with_freetype:
            replace_in_file(self, os.path.join(self.source_folder, "meson.build"),
                                  "freetype_required_version = '>= 9.7.3'",
                                  f"freetype_required_version = '>= {self.dependencies['freetype'].ref.version}'")
        meson = Meson(self)
        meson.configure()
        meson.build()

    def _fix_library_names(self, path):
        if is_msvc(self):
            for filename_old in glob.glob(os.path.join(path, "*.a")):
                root, _ = os.path.splitext(filename_old)
                folder, basename = os.path.split(root)
                rename(self, filename_old, os.path.join(folder, basename.replace("lib", "") + ".lib"))

    def package(self):
        meson = Meson(self)
        meson.install()
        self._fix_library_names(os.path.join(self.package_folder, "lib"))
        copy(self, "COPYING*", self.source_folder, os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        base_requirements = {"pixman::pixman"}
        base_system_libs = {}

        def add_component_and_base_requirements(component, requirements, system_libs=None):
            self.cpp_info.components[component].set_property("pkg_config_name", component)
            self.cpp_info.components[component].requires += ["cairo_"] + requirements
            base_requirements.update(set(requirements))
            if system_libs is not None:
                self.cpp_info.components[component].system_libs += system_libs
                base_system_libs.update(set(system_libs))

        self.cpp_info.set_property("pkg_config_name", "cairo-all-do-no-use")

        self.cpp_info.components["cairo_"].set_property("pkg_config_name", "cairo")
        self.cpp_info.components["cairo_"].libs = ["cairo"]
        self.cpp_info.components["cairo_"].includedirs.insert(0, os.path.join("include", "cairo"))

        if self.settings.os in ["Linux", "FreeBSD"]:
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
            add_component_and_base_requirements("cairo-png", ["libpng::libpng"])
            add_component_and_base_requirements("cairo-svg", ["libpng::libpng"])

        if self.options.with_fontconfig:
            add_component_and_base_requirements("cairo-fc", ["fontconfig::fontconfig"])

        if self.options.with_freetype:
            add_component_and_base_requirements("cairo-ft", ["freetype::freetype"])

        if self.options.get_safe("with_xlib"):
            add_component_and_base_requirements("cairo-xlib", ["xorg::x11", "xorg::xext"])

        if self.options.get_safe("with_xlib_xrender"):
            add_component_and_base_requirements("cairo-xlib-xrender", ["xorg::xrender"])

        if self.options.get_safe("with_xcb"):
            add_component_and_base_requirements("cairo-xcb", ["xorg::xcb", "xorg::xcb-render"])
            add_component_and_base_requirements("cairo-xcb-shm", ["xorg::xcb", "xorg::xcb-shm"])

            if self.options.get_safe("with_xlib"):
                add_component_and_base_requirements("cairo-xlib-xcb", ["xorg::x11-xcb"])

        if is_apple_os(self):
            self.cpp_info.components["cairo-quartz"].set_property("pkg_config_name", "cairo-quartz")
            self.cpp_info.components["cairo-quartz"].requires = ["cairo_"]

            self.cpp_info.components["cairo-quartz-image"].set_property("pkg_config_name", "cairo-quartz-image")
            self.cpp_info.components["cairo-quartz-image"].requires = ["cairo_"]

            self.cpp_info.components["cairo-quartz-font"].set_property("pkg_config_name", "cairo-quartz-font")
            self.cpp_info.components["cairo-quartz-font"].requires = ["cairo_"]

            self.cpp_info.components["cairo_"].frameworks += ["ApplicationServices", "CoreFoundation", "CoreGraphics"]

        if self.settings.os == "Windows":
            self.cpp_info.components["cairo-win32"].set_property("pkg_config_name", "cairo-win32")
            self.cpp_info.components["cairo-win32"].requires = ["cairo_"]

            self.cpp_info.components["cairo-win32-font"].set_property("pkg_config_name", "cairo-win32-font")
            self.cpp_info.components["cairo-win32-font"].requires = ["cairo_"]

            self.cpp_info.components["cairo_"].system_libs.extend(["gdi32", "msimg32", "user32"])

            if not self.options.shared:
                self.cpp_info.components["cairo_"].defines.append("CAIRO_WIN32_STATIC_BUILD=1")

        if self.options.get_safe("with_opengl"):
            if self.options.with_opengl == "desktop":
                add_component_and_base_requirements("cairo-gl", ["opengl::opengl"])

                if self.settings.os in ["Linux", "FreeBSD"]:
                    add_component_and_base_requirements("cairo-glx", ["opengl::opengl"])

                if self.settings.os == "Windows":
                    add_component_and_base_requirements("cairo-wgl", ["glext::glext", "wglext::wglext", "khrplatform::khrplatform"])

            elif self.options.with_opengl == "gles3":
                add_component_and_base_requirements("cairo-glesv3", [], ["GLESv2"])
            elif self.options.with_opengl == "gles2":
                add_component_and_base_requirements("cairo-glesv2", [], ["GLESv2"])
            if self.settings.os in ["Linux", "FreeBSD"]:
                add_component_and_base_requirements("cairo-egl", ["egl::egl"])

        if self.options.with_zlib:
            add_component_and_base_requirements("cairo-script", ["zlib::zlib"])
            add_component_and_base_requirements("cairo-ps", ["zlib::zlib"])
            add_component_and_base_requirements("cairo-pdf", ["zlib::zlib"])
            self.cpp_info.components["cairo-script-interpreter"].set_property("pkg_config_name", "cairo-script-interpreter")
            self.cpp_info.components["cairo-script-interpreter"].libs = ["cairo-script-interpreter"]
            self.cpp_info.components["cairo-script-interpreter"].requires = ["cairo_"]

            if self.options.with_png:
                add_component_and_base_requirements("cairo-xml", ["zlib::zlib"])
                add_component_and_base_requirements("cairo-util_", ["expat::expat"])

        if self.options.tee:
            self.cpp_info.components["cairo-tee"].set_property("pkg_config_name", "cairo-tee")
            self.cpp_info.components["cairo-tee"].requires = ["cairo_"]

        # util directory
        if self.options.with_glib:
            self.cpp_info.components["cairo-gobject"].set_property("pkg_config_name", "cairo-gobject")
            self.cpp_info.components["cairo-gobject"].libs = ["cairo-gobject"]
            self.cpp_info.components["cairo-gobject"].requires = ["cairo_", "glib::gobject-2.0", "glib::glib-2.0"]

        self.cpp_info.components["cairo_"].requires += list(base_requirements)
        self.cpp_info.components["cairo_"].system_libs += list(base_system_libs)
