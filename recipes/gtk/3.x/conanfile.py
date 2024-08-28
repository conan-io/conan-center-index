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
        "with_pango": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_wayland": True,
        "with_x11": True,
        "with_pango": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            # Fix duplicate definitions of DllMain
            self.options["gdk-pixbuf"].shared = True
            # Fix segmentation fault
            self.options["cairo"].shared = True
        if self.settings.os not in ["Linux", "FreeBSD"]:
            self.options.rm_safe("with_wayland")
            self.options.rm_safe("with_x11")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
        if self.settings.os in ["Linux", "FreeBSD"]:
            if self.options.with_wayland or self.options.with_x11:
                if not self.options.with_pango:
                    raise ConanInvalidConfiguration("with_pango option is mandatory when with_wayland or with_x11 is used")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # INFO: https://gitlab.gnome.org/GNOME/gtk/-/blob/4.10.0/gdk/gdktypes.h?ref_type=tags#L34-38
        self.requires("glib/2.78.3", transitive_headers=True, transitive_libs=True)
        # INFO: https://gitlab.gnome.org/GNOME/gtk/-/blob/4.10.0/gdk/gdkpixbuf.h?ref_type=tags#L32-33
        # Note: gdkpixbuf.h is deprecated in newer versions
        self.requires("gdk-pixbuf/2.42.10", transitive_headers=True, transitive_libs=True)
        self.requires("cairo/1.18.0", transitive_headers=True, transitive_libs=True)
        # https://gitlab.gnome.org/GNOME/gtk/-/blob/3.24.37/gtk/gtkwidget.h?ref_type=tags#L36
        self.requires("at-spi2-core/2.51.0", transitive_headers=True, transitive_libs=True)
        self.requires("libepoxy/1.5.10")
        if self.options.with_pango:
            self.requires("pango/1.51.0", transitive_headers=True, transitive_libs=True)
        if self.settings.os in ["Linux", "FreeBSD"]:
            if self.options.with_wayland:
                self.requires("wayland/1.22.0")
                self.requires("wayland-protocols/1.33")
                self.requires("xkbcommon/1.6.0")
            if self.options.with_x11:
                # https://gitlab.gnome.org/GNOME/gtk/-/blob/4.10.0/gdk/x11/gdkx11display.h#L35-36
                self.requires("xorg/system", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("MSVC support of this recipe requires at least gtk/4.2")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        self.tool_requires("glib/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()
        # Required for glib-compile-resources
        VirtualRunEnv(self).generate(scope="build")

        tc = MesonToolchain(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            tc.project_options["wayland_backend"] = "true" if self.options.with_wayland else "false"
            tc.project_options["x11_backend"] = "true" if self.options.with_x11 else "false"
        tc.project_options["introspection"] = "false"
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
        deps.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        # args = ["--wrap-mode=nofallback"]
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
        self.cpp_info.components["gdk-3.0"].requires = [
            "gdk-pixbuf::gdk-pixbuf",
            "libepoxy::libepoxy",
        ]
        if self.options.with_pango:
            self.cpp_info.components["gdk-3.0"].requires.extend(["pango::pango_", "pango::pangocairo"])
        if not is_msvc(self):
            self.cpp_info.components["gdk-3.0"].requires.extend(["cairo::cairo", "cairo::cairo-gobject"])
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["gdk-3.0"].requires.extend(["glib::gio-unix-2.0", "cairo::cairo-xlib"])
            if self.options.with_x11:
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
                ])
            if self.options.with_wayland:
                self.cpp_info.components["gdk-3.0"].requires.extend([
                    "wayland::wayland-client",
                    "wayland::wayland-cursor",
                    "wayland::wayland-egl",
                    "wayland-protocols::wayland-protocols",
                    "xkbcommon::xkbcommon",
                ])

        self.cpp_info.components["gtk+-3.0"].set_property("pkg_config_name", "gtk+-3.0")
        self.cpp_info.components["gtk+-3.0"].libs = ["gtk-3"]
        self.cpp_info.components["gtk+-3.0"].includedirs = [os.path.join("include", "gtk-3.0")]
        # skipping gtk+-3.0 requires that are covered by gdk-3.0
        self.cpp_info.components["gtk+-3.0"].requires = ["gdk-3.0", "glib::gio-2.0"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["gtk+-3.0"].requires.append("at-spi2-core::at-spi2-core")
        if self.options.with_pango:
            self.cpp_info.components["gtk+-3.0"].requires.append("pango::pangoft2")

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
