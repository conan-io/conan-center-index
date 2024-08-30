import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.56.0 <2 || >=2.0.6"


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
        "with_wayland": [True, False],
        "with_x11": [True, False],
        "with_introspection": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_wayland": True,
        "with_x11": True,
        "with_introspection": False,
    }
    no_copy_source = True

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
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
        if self.options.shared:
            self.options.rm_safe("fPIC")
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
        if self.options.get_safe("with_wayland"):
            self.requires("wayland/1.22.0")
            self.requires("wayland-protocols/1.33")
            self.requires("xkbcommon/1.6.0")
        if self.options.get_safe("with_x11"):
            # https://gitlab.gnome.org/GNOME/gtk/-/blob/4.10.0/gdk/x11/gdkx11display.h#L35-36
            self.requires("xorg/system", transitive_headers=True, transitive_libs=True)
            self.requires("fontconfig/2.15.0")

        # TODO: iso-codes
        # TODO: tracker-sparql-3.0
        # TODO: cloudproviders
        # TODO: sysprof-capture-4

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
        if self.options.with_introspection:
            self.tool_requires("gobject-introspection/1.78.1")  # for g-ir-scanner

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()
        # Required for glib-compile-resources
        VirtualRunEnv(self).generate(scope="build")

        tc = MesonToolchain(self)
        tc.project_options["wayland_backend"] = "true" if self.options.get_safe("with_wayland") else "false"
        tc.project_options["x11_backend"] = "true" if self.options.get_safe("with_x11") else "false"
        tc.project_options["introspection"] = "true" if self.options.with_introspection else "false"
        tc.project_options["gtk_doc"] = "false"
        tc.project_options["man"] = "false"
        tc.project_options["tests"] = "false"
        tc.project_options["examples"] = "false"
        tc.project_options["demos"] = "false"
        tc.project_options["datadir"] = os.path.join("res", "share")
        tc.project_options["localedir"] = os.path.join("res", "share", "locale")
        tc.project_options["sysconfdir"] = os.path.join("res", "etc")
        tc.generate()

        deps = PkgConfigDeps(self)
        if self.options.with_introspection:
            # gnome.generate_gir() in Meson looks for gobject-introspection-1.0.pc
            deps.build_context_activated = ["gobject-introspection"]
        deps.generate()

    def build(self):
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
        self.cpp_info.components["gdk-3.0"].requires = [
            "pango::pango_" if self.settings.os != "Windows" else "pango::pangowin32",
            "pango::pangocairo",
            "gdk-pixbuf::gdk-pixbuf",
            "cairo::cairo_",
            "cairo::cairo-gobject",
            "libepoxy::libepoxy",
            "fribidi::fribidi",
        ]
        if self.settings.os != "Windows":
            self.cpp_info.components["gdk-3.0"].requires.extend(["glib::gio-unix-2.0"])
        else:
            self.cpp_info.components["gdk-3.0"].requires.extend(["glib::gio-windows-2.0"])
        if self.options.get_safe("with_x11"):
            self.cpp_info.components["gdk-3.0"].requires.extend([
                "xorg::x11",
                "xorg::xext",
                "xorg::xi",
                "xorg::xrandr",
                "xorg::xcursor",
                "xorg::xfixes",
                "xorg::xcomposite",
                "xorg::xdamage",
                "xorg::xinerama",
                "cairo::cairo-xlib",
                "fontconfig::fontconfig",
            ])
        if self.options.get_safe("with_wayland"):
            self.cpp_info.components["gdk-3.0"].requires.extend([
                "wayland::wayland-client",
                "wayland::wayland-cursor",
                "wayland::wayland-egl",
                "wayland-protocols::wayland-protocols",
                "xkbcommon::xkbcommon",
            ])

        if self.options.with_introspection:
            self.buildenv_info.append_path("GI_GIR_PATH", os.path.join(self.package_folder, "res", "share", "gir-1.0"))
            self.env_info.GI_GIR_PATH.append(os.path.join(self.package_folder, "res", "share", "gir-1.0"))

        self.cpp_info.components["gtk+-3.0"].set_property("pkg_config_name", "gtk+-3.0")
        self.cpp_info.components["gtk+-3.0"].libs = ["gtk-3"]
        self.cpp_info.components["gtk+-3.0"].includedirs = [os.path.join("include", "gtk-3.0")]
        # skipping gtk+-3.0 requires that are covered by gdk-3.0
        self.cpp_info.components["gtk+-3.0"].requires = ["gdk-3.0", "glib::gio-2.0"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["gtk+-3.0"].requires.extend(["at-spi2-core::atk", "pango::pangoft2"])
            if self.options.with_x11:
                self.cpp_info.components["gtk+-3.0"].requires.append("at-spi2-core::atk-bridge")

        self.cpp_info.components["gtk+-unix-print-3.0"].set_property("pkg_config_name", "gtk+-unix-print-3.0")
        self.cpp_info.components["gtk+-unix-print-3.0"].requires = ["gtk+-3.0"]
        self.cpp_info.components["gtk+-unix-print-3.0"].includedirs = [os.path.join("include", "gtk-3.0", "unix-print")]

        self.cpp_info.components["gail-3.0"].set_property("pkg_config_name", "gail-3.0")
        self.cpp_info.components["gail-3.0"].libs = ["gailutil-3"]
        self.cpp_info.components["gail-3.0"].requires = ["gtk+-3.0"]
        self.cpp_info.components["gail-3.0"].includedirs = [os.path.join("include", "gail-3.0")]

        gdk_aliases = []
        gtk_aliases = []
        if self.options.get_safe("with_x11"):
            gdk_aliases.append("gdk-x11-3.0")
            gtk_aliases.append("gtk+-x11-3.0")
        if self.options.get_safe("with_wayland"):
            gdk_aliases.append("gdk-wayland-3.0")
            gtk_aliases.append("gtk+-wayland-3.0")
        if gdk_aliases:
            self.cpp_info.components["gdk-3.0"].set_property("pkg_config_aliases", gdk_aliases)
            self.cpp_info.components["gtk+-3.0"].set_property("pkg_config_aliases", gtk_aliases)
