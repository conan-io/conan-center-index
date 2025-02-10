import io
import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple.apple import is_apple_os
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv, Environment
from conan.tools.files import copy, get, replace_in_file, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
from conan.tools.system.package_manager import Apt

required_conan_version = ">=1.56.0 <2 || >=2.0.6"


class GtkConan(ConanFile):
    name = "gtk"
    description = "GTK is a multi-platform toolkit for creating graphical user interfaces"
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gtk.org"
    topics = ("gui", "widgets", "gnome")

    # The upstream meson file does not create a static library
    # See https://github.com/GNOME/gtk/commit/14f0a0addb9a195bad2f8651f93b95450b186bd6
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "enable_broadway_backend": [True, False],
        "with_wayland": [True, False],
        "with_x11": [True, False],
        "with_vulkan": [True, False],
        "with_introspection": [True, False],
        # Only available as system libs
        "with_gstreamer": [True, False],
        "with_cups": [True, False],
        "with_cpdb": [True, False],
        "with_cloudproviders": [True, False],
        "with_tracker": [True, False],
        "with_iso_codes": [True, False],
        # Unavailable since v4.13.7
        "with_ffmpeg": [True, False],
        # Deprecated
        "with_pango": ["deprecated", True, False],
        "with_cloudprint": ["deprecated", True, False],
    }
    default_options = {
        "enable_broadway_backend": False,
        "with_wayland": True,
        "with_x11": True,
        "with_vulkan": True,
        "with_introspection": False,
        "with_gstreamer": False,
        "with_cups": False,
        "with_cpdb": False,
        "with_cloudproviders": False,
        "with_tracker": False,
        "with_iso_codes": False,
        "with_ffmpeg": False,
        "with_pango": "deprecated",
        "with_cloudprint": "deprecated",
    }
    no_copy_source = True

    def config_options(self):
        if self.settings.os == "Windows":
            # Fix duplicate definitions of DllMain
            self.options["gdk-pixbuf"].shared = True
            # Fix segmentation fault
            self.options["cairo"].shared = True
        # Vulkan backend is enabled for all platforms except Apple OS-s,
        # which default to a macOS backend instead
        self.options.with_vulkan = not is_apple_os(self)
        self.options["pango"].with_cairo = True
        self.options["pango"].with_freetype = True
        self.options["pango"].with_fontconfig = True
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.with_wayland
            del self.options.with_x11
        if Version(self.version) >= "4.13.7":
            del self.options.with_ffmpeg
        if self.options.with_gstreamer:
            # elfutils required by system gstreamer conflicts with libelf dep of glib otherwise
            self.options["glib"].with_elf = False

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.options["cairo"].with_xlib = self.options.with_x11
            self.options["cairo"].with_xlib_xrender = self.options.with_x11
            self.options["cairo"].with_xcb = self.options.with_x11
            self.options["pango"].with_xft = self.options.with_x11
            self.options["libepoxy"].x11 = self.options.with_x11
            self.options["libepoxy"].glx = self.options.with_x11
            self.options["libepoxy"].egl = self.options.with_wayland
            if self.options.with_wayland:
                self.options["xkbcommon"].with_x11 = self.options.with_x11
                self.options["xkbcommon"].with_wayland = True

        if self.options.with_introspection:
            for dep in self._introspections_deps:
                self.options[dep].with_introspection = True

    @property
    def _introspections_deps(self):
        # Dependencies that must have introspection enabled as well if with_introspection is enabled
        # https://gitlab.gnome.org/GNOME/gtk/-/blob/4.15.6/gtk/meson.build?ref_type=tags#L1146
        # cairo-1.0 and Gio-2.0 are provided by gobject-introspection
        return ["gdk-pixbuf", "pango", "graphene"]

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.options.with_pango = True
        self.info.options.with_cloudprint = False

    def requirements(self):
        # INFO: https://gitlab.gnome.org/GNOME/gtk/-/blob/4.10.0/gdk/gdktypes.h?ref_type=tags#L34-38
        self.requires("glib/2.78.3", transitive_headers=True, transitive_libs=True)
        # INFO: https://gitlab.gnome.org/GNOME/gtk/-/blob/4.10.0/gdk/gdkpixbuf.h?ref_type=tags#L32-33
        # Note: gdkpixbuf.h is deprecated in newer versions
        self.requires("gdk-pixbuf/2.42.10", transitive_headers=True, transitive_libs=True)
        self.requires("pango/1.54.0", transitive_headers=True, transitive_libs=True)
        self.requires("cairo/1.18.0", transitive_headers=True, transitive_libs=True)
        # INFO: https://gitlab.gnome.org/GNOME/gtk/-/blob/4.10.0/gsk/gsktypes.h#L25
        self.requires("graphene/1.10.8", transitive_headers=True, transitive_libs=True)
        self.requires("libepoxy/1.5.10")
        self.requires("fribidi/1.0.13")
        self.requires("harfbuzz/8.3.0")
        self.requires("libpng/[>=1.6 <2]")
        self.requires("libtiff/4.6.0")
        self.requires("libjpeg/9e")
        if self.settings.os == "Linux" and Version(self.version) >= "4.13.2":
            self.requires("libdrm/2.4.120")
        if self.options.get_safe("with_wayland"):
            self.requires("wayland/1.22.0")
            self.requires("wayland-protocols/1.36")
            self.requires("xkbcommon/1.6.0")
        if self.options.get_safe("with_x11"):
            # https://gitlab.gnome.org/GNOME/gtk/-/blob/4.10.0/gdk/x11/gdkx11display.h#L35-36
            self.requires("xorg/system", transitive_headers=True, transitive_libs=True)
            self.requires("fontconfig/2.15.0")
        if self.options.with_vulkan:
            self.requires("vulkan-loader/1.3.290.0")
        if self.options.get_safe("with_ffmpeg"):
            self.requires("ffmpeg/5.0")
        # FIXME: gstreamer from CCI is currently not compatible
        # if self.options.with_gstreamer:
        #     self.requires("gstreamer/1.24.7")

        # TODO: iso-codes
        # TODO: tracker-sparql-3.0
        # TODO: cloudproviders
        # TODO: sysprof-capture-4
        # TODO: openprinting / cpdb-frontend
        # TODO: cups, colord

    def validate(self):
        if is_msvc(self):
            if not self.dependencies["gdk-pixbuf"].options.shared:
                raise ConanInvalidConfiguration("MSVC build requires shared gdk-pixbuf")
            if not self.dependencies["cairo"].options.shared:
                raise ConanInvalidConfiguration("MSVC build requires shared cairo")
        if self.settings.os not in ["Linux", "FreeBSD"]:
            if not self.options.with_x11 and not self.options.with_wayland:
                # Fails with 'Problem encountered: No backends enabled' otherwise
                raise ConanInvalidConfiguration("At least one of 'with_x11' or 'with_wayland' options must be enabled")
            if self.options.with_x11 and not self.dependencies["cairo"].options.with_xlib:
                raise ConanInvalidConfiguration("cairo must be built with '-o cairo/*:with_xlib=True' when 'with_x11' is enabled")
        if not self.dependencies["pango"].options.with_freetype:
            raise ConanInvalidConfiguration("pango must be built with '-o pango/*:with_freetype=True'")
        if self.options.with_pango != "deprecated":
            self.output.warning("The 'with_pango' option has been deprecated and will be removed in a future version")
        if self.options.with_cloudprint != "deprecated":
            self.output.warning("The 'with_cloudprint' option has been deprecated and will be removed in a future version. It never had any effect.")
        if self.options.with_introspection:
            for dep in self._introspections_deps:
                if not self.dependencies[dep].options.with_introspection:
                    raise ConanInvalidConfiguration(f"{dep} must be built with introspection enabled (-o {dep}/*:with_introspection=True)")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        self.tool_requires("glib/<host_version>")
        self.tool_requires("libxml2/[>=2.12.5 <3]")  # for xmllint
        self.tool_requires("sassc/3.6.2")
        if self.options.with_vulkan:
            self.tool_requires("shaderc/2024.1")  # for glslc
        if self.options.with_introspection:
            self.tool_requires("gobject-introspection/1.78.1")  # for g-ir-scanner

    @property
    def _apt_packages(self):
        packages = []
        if self.options.with_cups:
            packages.append("libcups2-dev")
            packages.append("libcolord-dev")
        if self.options.with_cpdb:
            packages.append("libcpdb-frontend-dev")
        if self.options.with_cloudproviders:
            packages.append("libcloudproviders-dev")
        if self.options.with_tracker:
            packages.append("libtracker-sparql-3.0-dev")
        if self.options.with_iso_codes:
            packages.append("iso-codes")
        if self.options.with_gstreamer:
            packages.append("libgstreamer1.0-dev")
            # for gstreamer-player-1.0
            packages.append("libgstreamer-plugins-bad1.0-dev")
            # for gstreamer-gl-1.0 and gstreamer-allocators-1.0
            packages.append("libgstreamer-plugins-base1.0-dev")
        return packages

    def system_requirements(self):
        Apt(self).install(self._apt_packages, update=True, check=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()
        # Required for glib-compile-resources
        VirtualRunEnv(self).generate(scope="build")

        enabled_disabled = lambda opt: "enabled" if opt else "disabled"
        tc = MesonToolchain(self)
        tc.project_options["wayland-backend"] = "true" if self.options.get_safe("with_wayland") else "false"
        tc.project_options["x11-backend"] = "true" if self.options.get_safe("with_x11") else "false"
        tc.project_options["broadway-backend"] = "true" if self.options.enable_broadway_backend else "false"
        tc.project_options["vulkan"] = enabled_disabled(self.options.with_vulkan)
        tc.project_options["media-gstreamer"] = enabled_disabled(self.options.with_gstreamer)
        if Version(self.version) < "4.13.7":
            tc.project_options["media-ffmpeg"] = enabled_disabled(self.options.with_ffmpeg)
        tc.project_options["print-cups"] = enabled_disabled(self.options.with_cups)
        tc.project_options["colord"] = enabled_disabled(self.options.with_cups)
        if Version(self.version) >= "4.10.0":
            tc.project_options["print-cpdb"] = enabled_disabled(self.options.with_cpdb)
        tc.project_options["cloudproviders"] = enabled_disabled(self.options.with_cloudproviders)
        tc.project_options["tracker"] = enabled_disabled(self.options.with_tracker)
        tc.project_options["introspection"] = enabled_disabled(self.options.with_introspection)

        if self.version == "4.7.0":
            tc.project_options["gtk_doc"] = "false"
            tc.project_options["update_screenshots"] = "false"
            tc.project_options["demos"] = "false"
        else:
            tc.project_options["documentation"] = "false"
            tc.project_options["screenshots"] = "false"
            tc.project_options["build-demos"] = "false"
            tc.project_options["build-testsuite"] = "false"
        tc.project_options["man-pages"] = "false"
        tc.project_options["build-tests"] = "false"
        tc.project_options["build-examples"] = "false"

        tc.project_options["datadir"] = os.path.join("res", "share")
        tc.project_options["localedir"] = os.path.join("res", "share", "locale")
        tc.project_options["sysconfdir"] = os.path.join("res", "etc")

        if self._apt_packages:
            # Don't force generators folder as the only PKG_CONFIG_PATH if system packages are in use.
            tc.pkg_config_path = None
            env = Environment()
            env.define_path("PKG_CONFIG_PATH", self.generators_folder)
            env.append_path("PKG_CONFIG_PATH", self._get_system_pkg_config_paths())
            env.vars(self).save_script("conan_pkg_config_path")

        tc.generate()

        deps = PkgConfigDeps(self)
        if self.options.with_introspection:
            # gnome.generate_gir() in Meson looks for gobject-introspection-1.0.pc
            deps.build_context_activated = ["gobject-introspection"]
        deps.generate()

    def _get_system_pkg_config_paths(self):
        # Global PKG_CONFIG_PATH is generally not filled by default, so ask for the default paths from pkg-config instead.
        # Assumes that pkg-config is installed system-wide.
        pkg_config = self.conf.get("tools.gnu:pkg_config", default="pkg-config", check_type=str)
        output = io.StringIO()
        self.run(f"{pkg_config} --variable pc_path pkg-config", output, scope=None)
        return output.getvalue().strip()

    def _patch_sources(self):
        if "4.6.2" <= Version(self.version) < "4.9.2":
            replace_in_file(self, os.path.join(self.source_folder, "meson.build"), "dependency(is_msvc_like ? ", "dependency(false ? ", strict=not self.no_copy_source)

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"), recursive=True)
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"), recursive=True)

    def package_info(self):
        # https://gitlab.gnome.org/GNOME/gtk/-/blob/4.15.6/meson.build?ref_type=tags#L841-883
        self.cpp_info.components["gtk4"].set_property("pkg_config_name", "gtk4")
        self.cpp_info.components["gtk4"].libs = ["gtk-4"]
        self.cpp_info.components["gtk4"].includedirs.append(os.path.join("include", "gtk-4.0"))
        self.cpp_info.components["gtk4"].resdirs = ["res", os.path.join("res", "share")]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["gtk4"].system_libs = ["m", "rt"]
        # https://gitlab.gnome.org/GNOME/gtk/-/blob/4.15.6/gdk/meson.build#L221-240
        # https://gitlab.gnome.org/GNOME/gtk/-/blob/4.15.6/gtk/meson.build#L1000-1015
        self.cpp_info.components["gtk4"].requires = [
            "glib::gio-2.0",
            "glib::glib-2.0",
            "glib::gmodule-2.0",
            "glib::gobject-2.0",
            "gdk-pixbuf::gdk-pixbuf",
            "cairo::cairo_",
            "cairo::cairo-gobject",
            "pango::pango_" if self.settings.os != "Windows" else "pango::pangowin32",
            "pango::pangocairo",
            "fribidi::fribidi",
            "graphene::graphene-gobject-1.0",
            "harfbuzz::harfbuzz_",
            "harfbuzz::subset",
            "libepoxy::libepoxy",
            "libjpeg::libjpeg",
            "libpng::libpng",
            "libtiff::libtiff",
        ]
        if self.settings.os == "Windows":
            self.cpp_info.components["gtk4"].requires.extend(["glib::gio-windows-2.0"])
        else:
            self.cpp_info.components["gtk4"].requires.extend(["glib::gio-unix-2.0"])

        if self.settings.os == "Linux" and Version(self.version) >= "4.13.2":
            self.cpp_info.components["gtk4"].requires.append("libdrm::libdrm")

        if self.options.with_vulkan:
            self.cpp_info.components["gtk4"].requires.append("vulkan-loader::vulkan-loader")

        if self.options.with_introspection:
            self.buildenv_info.append_path("GI_GIR_PATH", os.path.join(self.package_folder, "res", "share", "gir-1.0"))
            self.env_info.GI_GIR_PATH.append(os.path.join(self.package_folder, "res", "share", "gir-1.0"))

        # if self.options.with_gstreamer:
        #     # https://gitlab.gnome.org/GNOME/gtk/-/blob/4.15.6/modules/media/meson.build#L11
        #     self.cpp_info.components["gtk4"].requires.extend([
        #         "gstreamer::gstreamer-player-1.0",
        #         "gstreamer::gstreamer-gl-1.0",
        #         "gstreamer::gstreamer-allocators-1.0",
        #     ])
        if self.options.get_safe("with_ffmpeg"):
            self.cpp_info.components["gtk4"].requires.append("ffmpeg::ffmpeg")

        # TODO:
        # if self.options.with_cups:
        #     self.cpp_info.components["gtk4"].requires.extend(["cups::cups", "colord::colord"])
        # if self.options.with_cpdb:
        #     self.cpp_info.components["gtk4"].requires.append("cpdb::cpdb")
        # if self.options.with_cloudproviders:
        #     self.cpp_info.components["gtk4"].requires.append("cloudproviders::cloudproviders")

        if self.options.enable_broadway_backend:
            self.cpp_info.components["gtk4-broadway"].set_property("pkg_config_name", "gtk4-broadway")
            self.cpp_info.components["gtk4-broadway"].requires = ["gtk4"]
            # https://gitlab.gnome.org/GNOME/gtk/-/blob/4.15.6/gdk/broadway/meson.build#L66
            if self.settings.os == "Windows":
                self.cpp_info.components["gtk4"].system_libs.append("ws2_32")

        # https://gitlab.gnome.org/GNOME/gtk/-/blob/4.15.6/meson.build?ref_type=tags#L841-883
        if self.options.get_safe("with_x11"):
            self.cpp_info.components["gtk4-x11"].set_property("pkg_config_name", "gtk4-x11")
            self.cpp_info.components["gtk4-x11"].requires = ["gtk4"]
            # https://gitlab.gnome.org/GNOME/gtk/-/blob/4.15.6/gdk/x11/meson.build#L63-73
            self.cpp_info.components["gtk4"].requires.extend([
                "xorg::xrandr",
                "xorg::x11",
                "xorg::xrender",
                "xorg::xi",
                "xorg::xext",
                "xorg::xcursor",
                "xorg::xdamage",
                "xorg::xfixes",
                "xorg::xinerama",
                "fontconfig::fontconfig",
            ])

        if self.options.get_safe("with_wayland"):
            self.cpp_info.components["gtk4-wayland"].set_property("pkg_config_name", "gtk4-wayland")
            self.cpp_info.components["gtk4-wayland"].requires = ["gtk4"]
            # https://gitlab.gnome.org/GNOME/gtk/-/blob/4.15.6/gdk/wayland/meson.build#L44-50
            self.cpp_info.components["gtk4"].requires.extend([
                "xkbcommon::xkbcommon",
                "wayland::wayland-client",
                "wayland::wayland-egl",
                "wayland-protocols::wayland-protocols",
            ])

        if is_apple_os(self):
            self.cpp_info.components["gtk4-macos"].set_property("pkg_config_name", "gtk4-macos")
            self.cpp_info.components["gtk4-macos"].requires = ["gtk4"]
            # https://gitlab.gnome.org/GNOME/gtk/-/blob/4.15.6/gdk/macos/meson.build#L46-55
            self.cpp_info.components["gtk4"].frameworks.extend([
                "AppKit",
                "Carbon",
                "CoreVideo",
                "CoreServices",
                "Foundation",
                "IOSurface",
                "OpenGL",
                "QuartzCore",
            ])

        if self.settings.os == "Windows":
            self.cpp_info.components["gtk4-win32"].set_property("pkg_config_name", "gtk4-win32")
            self.cpp_info.components["gtk4-win32"].requires = ["gtk4"]
            # https://gitlab.gnome.org/GNOME/gtk/-/blob/4.15.6/gdk/win32/meson.build#L60-64
            self.cpp_info.components["gtk4"].system_libs.extend(["hid", "opengl32"])

        if self.settings.os != "Windows":
            # https://gitlab.gnome.org/GNOME/gtk/-/blob/4.15.6/meson.build?ref_type=tags#L897-907
            self.cpp_info.components["gtk4-atspi"].set_property("pkg_config_name", "gtk4-atspi")
            self.cpp_info.components["gtk4-atspi"].requires = ["gtk4"]

            # https://gitlab.gnome.org/GNOME/gtk/-/blob/4.15.6/meson.build?ref_type=tags#L909-919
            self.cpp_info.components["gtk4-unix-print"].set_property("pkg_config_name", "gtk4-unix-print")
            self.cpp_info.components["gtk4-unix-print"].requires = ["gtk4"]
            self.cpp_info.components["gtk4-unix-print"].includedirs.append(os.path.join("include", "gtk-4.0", "unix-print"))

        # TODO: add the following info to all generated .pc files:
        # targets=wayland x11
        # gtk_binary_version=4.0.0
        # gtk_host=x86_64-linux
