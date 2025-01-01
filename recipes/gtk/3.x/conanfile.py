import io
import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.env import Environment
from conan.tools.files import copy, get, rm, rmdir, export_conandata_patches, apply_conandata_patches, rename
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.microsoft import is_msvc
from conan.tools.system.package_manager import Apt

required_conan_version = ">=2.0.9"


class GtkConan(ConanFile):
    name = "gtk"
    description = "GTK is a multi-platform toolkit for creating graphical user interfaces"
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gtk.org"
    topics = ("gui", "widgets", "gnome")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_broadway_backend": [True, False],
        "with_wayland": [True, False],
        "with_x11": [True, False],
        "with_introspection": [True, False],
        # Only available as system libs
        "with_cups": [True, False],
        "with_cloudproviders": [True, False],
        "with_tracker": [True, False],
        "with_iso_codes": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_broadway_backend": False,
        "with_wayland": True,
        "with_x11": True,
        "with_introspection": False,
        "with_cups": False,
        "with_cloudproviders": False,
        "with_tracker": False,
        "with_iso_codes": False,
    }
    no_copy_source = True
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            # Fix duplicate definitions of DllMain
            self.options["gdk-pixbuf"].shared = True
            # Fix segmentation fault
            self.options["cairo"].shared = True
        self.options["pango"].with_cairo = True
        if self.settings.os not in ["Linux", "FreeBSD"]:
            self.options.rm_safe("with_wayland")
            self.options.rm_safe("with_x11")
        else:
            self.options["pango"].with_freetype = True

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.options["cairo"].with_xlib = self.options.with_x11
            self.options["cairo"].with_xlib_xrender = self.options.with_x11
            self.options["cairo"].with_xcb = self.options.with_x11
            self.options["pango"].with_xft = self.options.with_x11
            self.options["at-spi2-core"].with_x11 = self.options.with_x11
            self.options["libepoxy"].x11 = self.options.with_x11
            self.options["libepoxy"].glx = self.options.with_x11
            self.options["libepoxy"].egl = self.options.with_wayland
            if self.options.with_wayland:
                self.options["xkbcommon"].with_x11 = self.options.with_x11
                self.options["xkbcommon"].with_wayland = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("glib/2.78.3", transitive_headers=True, transitive_libs=True)
        self.requires("gdk-pixbuf/2.42.10", transitive_headers=True, transitive_libs=True)
        self.requires("pango/1.54.0", transitive_headers=True, transitive_libs=True)
        self.requires("cairo/1.18.0", transitive_headers=True, transitive_libs=True)
        # https://gitlab.gnome.org/GNOME/gtk/-/blob/3.24.37/gtk/gtkwidget.h?ref_type=tags#L36
        self.requires("at-spi2-core/2.51.0", transitive_headers=True, transitive_libs=True)
        self.requires("libepoxy/1.5.10")
        self.requires("fribidi/1.0.13")
        self.requires("harfbuzz/8.3.0")
        if self.options.get_safe("with_wayland"):
            self.requires("wayland/1.22.0")
            self.requires("xkbcommon/1.6.0")
        if self.options.get_safe("with_x11"):
            # https://gitlab.gnome.org/GNOME/gtk/-/blob/3.24.37/gdk/x11/gdkx11display.h#L34-35
            # Only the xorg::x11 component actually requires transitive headers/libs.
            self.requires("xorg/system", transitive_headers=True, transitive_libs=True)
            self.requires("fontconfig/2.15.0")

        # TODO: fix libintl support on macOS by using gnuintl from gettext
        # if self.settings.os != "Linux":
        #     # for Linux, gettext is provided by libc
        #     self.requires("libgettext/0.22", transitive_headers=True, transitive_libs=True)

        # TODO: iso-codes
        # TODO: tracker-sparql-3.0
        # TODO: cloudproviders
        # TODO: sysprof-capture-4
        # TODO: cups, colord

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("MSVC support of this recipe requires at least gtk/4.2")
        if not self.dependencies["pango"].options.with_cairo:
            raise ConanInvalidConfiguration("pango must be built with '-o pango/*:with_cairo=True'")
        if self.settings.os in ["Linux", "FreeBSD"]:
            if not self.options.with_x11 and not self.options.with_wayland:
                # Fails with 'Problem encountered: No backends enabled' otherwise
                raise ConanInvalidConfiguration("At least one of 'with_x11' or 'with_wayland' options must be enabled")
            if self.options.with_x11 and not self.dependencies["cairo"].options.with_xlib:
                raise ConanInvalidConfiguration("cairo must be built with '-o cairo/*:with_xlib=True' when 'with_x11' is enabled")
        if self.options.get_safe("with_x11") or self.options.get_safe("with_wayland"):
            if not self.dependencies["pango"].options.with_freetype:
                raise ConanInvalidConfiguration(f"pango must be built with '-o pango/*:with_freetype=True' on {self.settings.os}")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        self.tool_requires("glib/<host_version>")
        self.tool_requires("gettext/0.22.5")
        if self.options.get_safe("with_wayland"):
            self.tool_requires("wayland-protocols/1.33")
        if self.options.with_introspection:
            self.tool_requires("gobject-introspection/1.78.1")  # for g-ir-scanner

    @property
    def _apt_packages(self):
        packages = []
        if self.options.with_cups:
            packages.append("libcups2-dev")
            packages.append("libcolord-dev")
        if self.options.with_cloudproviders:
            packages.append("libcloudproviders-dev")
        if self.options.with_tracker:
            packages.append("libtracker-sparql-3.0-dev")
        if self.options.with_iso_codes:
            packages.append("iso-codes")
        return packages

    def system_requirements(self):
        Apt(self).install(self._apt_packages, update=True, check=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        true_false = lambda opt: "true" if opt else "false"
        tc = MesonToolchain(self)
        tc.project_options["wayland_backend"] = true_false(self.options.get_safe("with_wayland"))
        tc.project_options["x11_backend"] = true_false(self.options.get_safe("with_x11"))
        tc.project_options["broadway_backend"] = true_false(self.options.enable_broadway_backend)
        tc.project_options["print_backends"] = "file,lpr" + (",cups" if self.options.with_cups else "")
        tc.project_options["colord"] = "yes" if self.options.with_cups else "no"
        tc.project_options["cloudproviders"] = true_false(self.options.with_cloudproviders)
        tc.project_options["tracker3"] = true_false(self.options.with_tracker)
        tc.project_options["introspection"] = true_false(self.options.with_introspection)

        tc.project_options["gtk_doc"] = "false"
        tc.project_options["man"] = "false"
        tc.project_options["tests"] = "false"
        tc.project_options["examples"] = "false"
        tc.project_options["demos"] = "false"

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
        if self.options.get_safe("with_wayland"):
            deps.build_context_activated.append("wayland-protocols")
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

    def build(self):
        apply_conandata_patches(self)
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
        self.cpp_info.components["gdk-3.0"].set_property("pkg_config_name", "gdk-3.0")
        self.cpp_info.components["gdk-3.0"].libs = ["gdk-3"]
        self.cpp_info.components["gdk-3.0"].includedirs = [os.path.join("include", "gtk-3.0")]
        self.cpp_info.components["gdk-3.0"].resdirs = ["res", os.path.join("res", "share")]
        # https://gitlab.gnome.org/GNOME/gtk/-/blob/3.24.43/gdk/meson.build#L200-212
        self.cpp_info.components["gdk-3.0"].requires = [
            "glib::gio-unix-2.0" if self.settings.os != "Windows" else "glib::gio-windows-2.0",
            "glib::glib-2.0",
            "pango::pango_" if self.settings.os != "Windows" else "pango::pangowin32",
            "pango::pangocairo",
            "cairo::cairo_",
            "cairo::cairo-gobject",
            "fribidi::fribidi",
            "gdk-pixbuf::gdk-pixbuf",
            "libepoxy::libepoxy",
        ]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["gdk-3.0"].system_libs = ["m", "rt"]
        elif self.settings.os == "Windows":
            # https://gitlab.gnome.org/GNOME/gtk/-/blob/3.24.43/gdk/meson.build#L215-221
            self.cpp_info.components["gdk-3.0"].system_libs = ["advapi32", "comctl32", "dwmapi", "imm32", "opengl32", "setupapi", "winmm"]

        self.cpp_info.components["gtk+-3.0"].set_property("pkg_config_name", "gtk+-3.0")
        self.cpp_info.components["gtk+-3.0"].libs = ["gtk-3"]
        self.cpp_info.components["gtk+-3.0"].includedirs = [os.path.join("include", "gtk-3.0")]
        self.cpp_info.components["gtk+-3.0"].requires = ["gdk-3.0"]
        # https://gitlab.gnome.org/GNOME/gtk/-/blob/3.24.43/gtk/meson.build#L834-851
        self.cpp_info.components["gtk+-3.0"].requires.extend([
            "glib::gmodule-2.0",
            "glib::glib-2.0",
            "glib::gobject-2.0",
            "glib::gio-unix-2.0" if self.settings.os != "Windows" else "glib::gio-windows-2.0",
            "pango::pango_" if self.settings.os != "Windows" else "pango::pangowin32",
            "pango::pangocairo",
            "cairo::cairo_",
            "cairo::cairo-gobject",
            "harfbuzz::harfbuzz_",
            "fribidi::fribidi",
            "gdk-pixbuf::gdk-pixbuf",
            "at-spi2-core::atk",
            "libepoxy::libepoxy",
        ])

        # TODO:
        # if self.options.with_cups:
        #     self.cpp_info.components["gtk+-3.0"].requires.extend(["cups::cups", "colord::colord"])
        # if self.options.with_cloudproviders:
        #     self.cpp_info.components["gtk+-3.0"].requires.append("cloudproviders::cloudproviders")
        # if self.options.with_tracker:
        #     self.cpp_info.components["gtk+-3.0"].requires.append("tracker-sparql::tracker-sparql")

        if self.options.enable_broadway_backend:
            self.cpp_info.components["gdk-broadway-3.0"].set_property("pkg_config_name", "gdk-broadway-3.0")
            self.cpp_info.components["gdk-broadway-3.0"].requires = ["gdk-3.0"]
            self.cpp_info.components["gtk-broadway-3.0"].set_property("pkg_config_name", "gtk+-broadway-3.0")
            self.cpp_info.components["gtk-broadway-3.0"].requires = ["gtk+-3.0"]
            # https://gitlab.gnome.org/GNOME/gtk/-/blob/3.24.43/gdk/broadway/meson.build#L70
            if self.settings.os == "Windows":
                self.cpp_info.components["gdk-3.0"].system_libs.append("ws2_32")

        if self.options.get_safe("with_x11"):
            self.cpp_info.components["gdk-x11-3.0"].set_property("pkg_config_name", "gdk-x11-3.0")
            self.cpp_info.components["gdk-x11-3.0"].requires = ["gdk-3.0"]
            self.cpp_info.components["gtk-x11-3.0"].set_property("pkg_config_name", "gtk+-x11-3.0")
            self.cpp_info.components["gtk-x11-3.0"].requires = ["gtk+-3.0"]
            # https://gitlab.gnome.org/GNOME/gtk/-/blob/3.24.43/gdk/x11/meson.build#L59-70
            self.cpp_info.components["gdk-3.0"].requires.extend([
                "xorg::xrender",
                "xorg::xi",
                "xorg::xext",
                "xorg::x11",
                "xorg::xcursor",
                "xorg::xdamage",
                "xorg::xfixes",
                "xorg::xcomposite",
                "xorg::xrandr",
                "xorg::xinerama",
            ])
            # https://gitlab.gnome.org/GNOME/gtk/-/blob/3.24.43/meson.build#L497-500
            self.cpp_info.components["gdk-3.0"].requires.append("cairo::cairo-xlib")
            # https://gitlab.gnome.org/GNOME/gtk/-/blob/3.24.43/meson.build#L444-445
            self.cpp_info.components["gdk-3.0"].requires.append("fontconfig::fontconfig")
            self.cpp_info.components["gtk+-3.0"].requires.append("at-spi2-core::atk-bridge")
            self.cpp_info.components["gtk+-3.0"].requires.append("pango::pangoft2")

        if self.options.get_safe("with_wayland"):
            self.cpp_info.components["gdk-wayland-3.0"].set_property("pkg_config_name", "gdk-wayland-3.0")
            self.cpp_info.components["gdk-wayland-3.0"].requires = ["gdk-3.0"]
            self.cpp_info.components["gtk-wayland-3.0"].set_property("pkg_config_name", "gtk+-wayland-3.0")
            self.cpp_info.components["gtk-wayland-3.0"].requires = ["gtk+-3.0"]
            # https://gitlab.gnome.org/GNOME/gtk/-/blob/3.24.43/gdk/wayland/meson.build#L29-36
            self.cpp_info.components["gdk-3.0"].requires.extend([
                "xkbcommon::xkbcommon",
                "wayland::wayland-client",
                "wayland::wayland-cursor",
                "wayland::wayland-egl",
            ])
            self.cpp_info.components["gtk+-3.0"].requires.append("pango::pangoft2")

        if is_apple_os(self):
            self.cpp_info.components["gdk-quartz-3.0"].set_property("pkg_config_name", "gdk-quartz-3.0")
            self.cpp_info.components["gdk-quartz-3.0"].requires = ["gdk-3.0"]
            self.cpp_info.components["gtk-quartz-3.0"].set_property("pkg_config_name", "gtk+-quartz-3.0")
            self.cpp_info.components["gtk-quartz-3.0"].requires = ["gtk+-3.0"]
            # https://gitlab.gnome.org/GNOME/gtk/-/blob/3.24.43/gdk/quartz/meson.build#L48-53
            self.cpp_info.components["gdk-3.0"].requires.append("cairo::cairo-quartz")
            self.cpp_info.components["gdk-3.0"].frameworks.extend([
                "CoreGraphics",
                "AppKit",
                "Cocoa",
                "Carbon",
                "QuartzCore",
                "IOSurface",
            ])

        if self.settings.os == "Windows":
            self.cpp_info.components["gdk-win32-3.0"].set_property("pkg_config_name", "gdk-win32-3.0")
            self.cpp_info.components["gdk-win32-3.0"].requires = ["gdk-3.0"]
            self.cpp_info.components["gtk-win32-3.0"].set_property("pkg_config_name", "gtk+-win32-3.0")
            self.cpp_info.components["gtk-win32-3.0"].requires = ["gtk+-3.0"]
            # https://gitlab.gnome.org/GNOME/gtk/-/blob/3.24.43/gdk/win32/meson.build#L53-56
            self.cpp_info.components["gdk-3.0"].requires.append("cairo::cairo-win32")
            self.cpp_info.components["gdk-3.0"].system_libs.extend(["hid", "opengl32"])

        if self.settings.os != "Windows":
            self.cpp_info.components["gtk+-unix-print-3.0"].set_property("pkg_config_name", "gtk+-unix-print-3.0")
            self.cpp_info.components["gtk+-unix-print-3.0"].requires = ["gtk+-3.0"]
            self.cpp_info.components["gtk+-unix-print-3.0"].includedirs = [os.path.join("include", "gtk-3.0", "unix-print")]

        self.cpp_info.components["gail-3.0"].set_property("pkg_config_name", "gail-3.0")
        self.cpp_info.components["gail-3.0"].libs = ["gailutil-3"]
        self.cpp_info.components["gail-3.0"].requires = ["gtk+-3.0"]
        self.cpp_info.components["gail-3.0"].includedirs = [os.path.join("include", "gail-3.0")]

        if self.options.with_introspection:
            self.buildenv_info.append_path("GI_GIR_PATH", os.path.join(self.package_folder, "res", "share", "gir-1.0"))
            self.buildenv_info.append_path("GI_TYPELIB_PATH", os.path.join(self.package_folder, "lib", "girepository-1.0"))

        # https://gitlab.gnome.org/GNOME/gtk/-/blob/3.24.43/meson.build?ref_type=tags#L886-887
        pkgconfig_variables = {
            "targets": " ".join(self._enabled_backends),
            "gtk_binary_version": "3.0.0",
            "gtk_host": f"{self._host_arch}-{self._host_os}",
        }
        extra_content = "\n".join(f"{key}={value}" for key, value in pkgconfig_variables.items())
        for _, component in self.cpp_info.components.items():
            component.set_property("pkg_config_custom_content", extra_content)

    @property
    def _enabled_backends(self):
        # https://gitlab.gnome.org/GNOME/gtk/-/blob/3.24.43/meson.build?ref_type=tags#L954-965
        backends = []
        if self.options.enable_broadway_backend:
            backends.append("broadway")
        if self.settings.os in ["Linux", "FreeBSD"]:
            if self.options.with_x11:
                backends.append("x11")
            if self.options.with_wayland:
                backends.append("wayland")
        elif is_apple_os(self):
            backends.append("quartz")
        elif self.settings.os == "Windows":
            backends.append("win32")
        return backends

    @property
    def _host_arch(self):
        # https://mesonbuild.com/Reference-tables.html#cpu-families
        if self.settings.arch == "armv8":
            return "aarch64"
        elif str(self.settings.arch).startswith("arm"):
            return "arm"
        return str(self.settings.arch).lower()

    @property
    def _host_os(self):
        # https://mesonbuild.com/Reference-tables.html#operating-system-names
        if is_apple_os(self):
            return "darwin"
        return str(self.settings.os).lower()
