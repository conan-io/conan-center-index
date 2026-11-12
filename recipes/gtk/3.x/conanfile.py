from conan import ConanFile
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.gnu import PkgConfigDeps
from conan.tools.files import get, copy, rmdir, export_conandata_patches, apply_conandata_patches
from conan.tools.layout import basic_layout
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.scm import Version
import os


required_conan_version = ">=2.4"


class Gtk4Conan(ConanFile):
    name = "gtk"
    description = "libraries used for creating graphical user interfaces for applications."
    topics = ("gtk", "widgets")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gtk.org"
    license = "LGPL-2.1-or-later"
    package_type = "library"
    languages = "C"
    settings = "os", "arch", "compiler", "build_type"
    implements = ["auto_shared_fpic"]
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_wayland": [True, False],
        "with_x11": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_wayland": False,
        "with_x11": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.with_wayland
            del self.options.with_x11

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        # INFO: GDK build requires glib-compile-resources tool
        self.tool_requires("glib/<host_version>")
        if self.options.get_safe("with_wayland", False):
            # INFO: meson.build:716 wayland-scanner is needed
            self.tool_requires("wayland/<host_version>")
            self.tool_requires("wayland-protocols/[>=1.42 <2]")

    def requirements(self):
        # INFO: gdk/gdkconfig.h:8:#include <glib.h>
        self.requires("glib/[>=2.82 <3]", transitive_headers=True)
        # INFO: gdk/gdkpixbuf.h:33:#include <gdk-pixbuf/gdk-pixbuf.h>
        self.requires("gdk-pixbuf/[>=2.42 <3]", transitive_headers=True)
        # INFO: gtk-3.0/gdk/gdkscreen.h:29:#include <cairo.h>
        self.requires("cairo/[>=1.18 <2]", transitive_headers=True)
        # INFO: gdk/gdkcairo.h:30:#include <pango/pangocairo.h>
        self.requires("pango/[>=1.50.7 <2]", transitive_headers=True)
        # INFO: gtk/gtkwidget.h:36:#include <atk/atk.h>
        self.requires("at-spi2-core/[>=2.53.1 <3]", transitive_headers=True)
        self.requires("fribidi/1.0.13")
        self.requires("libepoxy/1.5.10")
        if self.settings.os == "Linux":
            if self.options.with_wayland:
                self.requires("xkbcommon/[>=1.5.0 <2]")
                self.requires("wayland/[>=1.23 <2]")
            if self.options.with_x11:
                self.requires("xorg/system")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = MesonToolchain(self)
        # GDK backends
        tc.project_options["wayland_backend"] = bool(self.options.get_safe("with_wayland", False))
        tc.project_options["x11_backend"] = bool(self.options.get_safe("with_x11", False))
        tc.project_options["win32_backend"] = self.settings.os == "Windows"
        tc.project_options["quartz_backend"] = self.settings.os == "Macos"
        # Print backends
        tc.project_options["colord"] = "no"
        # Optional features
        tc.project_options["xinerama"] = "no"
        tc.project_options["cloudproviders"] = False
        tc.project_options["profiler"] = False
        tc.project_options["tracker3"] = False
        # Introspection
        tc.project_options["introspection"] = False
        # Documentation
        tc.project_options["gtk_doc"] = False
        tc.project_options["man"] = False
        # Demos, examples and tests
        tc.project_options["demos"] = False
        tc.project_options["examples"] = False
        tc.project_options["tests"] = False
        tc.project_options["installed_tests"] = False
        tc.generate()

        deps = PkgConfigDeps(self)
        if self.options.get_safe("with_wayland", False):
            deps.build_context_activated = ["wayland-protocols"]

        # INFO: glib-compile-resources needs to load libgio-2.0 shared library at runtime
        # Meson gnome.compile_resources uses pkg-config to find gio-2.0.pc file
        # Adjust pkg_config_custom_content to point to build context binary directory
        glib_gio_pkg_config_vars = self.dependencies.host['glib'].cpp_info.components['gio-2.0'].get_property("pkg_config_custom_content", None)
        if glib_gio_pkg_config_vars:
            glib_build_context_bindir = self.dependencies.build['glib'].cpp_info.bindirs[0]
            glib_gio_pkg_config_vars = glib_gio_pkg_config_vars.replace("${bindir}", glib_build_context_bindir)
            deps.set_property("glib::gio-2.0", "pkg_config_custom_content", glib_gio_pkg_config_vars)

        deps.generate()

    def validate(self):
        if self.settings.os == "Linux" and not (self.options.with_wayland or self.options.with_x11):
            raise ConanInvalidConfiguration("At least one of backends '-o &:with_wayland' or '-o &:with_x11' options must be True on Linux")

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        meson = Meson(self)
        meson.install()
        fix_apple_shared_install_name(self)

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "etc"))

    def package_info(self):
        gtk_targets = []
        if self.options.get_safe("with_x11", False):
            gtk_targets.append("x11")
        if self.options.get_safe("with_wayland", False):
            gtk_targets.append("wayland")
        if self.settings.os == "Windows":
            gtk_targets.append("win32")
        if self.settings.os == "Macos":
            gtk_targets.append("quartz")
        property_os = "darwin" if self.settings.os == "Macos" else str(self.settings.os).lower()
        property_arch = "aarch64" if property_os == "darwin" and self.settings.arch == "armv8" else str(self.settings.arch)
        pkgconfig_vars = {
            "targets": gtk_targets,
            "gtk_binary_version": f"{Version(self.version).major}.0.0",
            "gtk_host": f"{property_arch}-{property_os}"
        }

        self.cpp_info.components["gdk-3"].libs = ["gdk-3"]
        self.cpp_info.components["gdk-3"].set_property("pkg_config_name", "gdk+-3.0")
        self.cpp_info.components["gdk-3"].set_property("pkg_config_custom_content", pkgconfig_vars)
        self.cpp_info.components["gdk-3"].includedirs.append(os.path.join("include", "gtk-3.0"))
        self.cpp_info.components["gdk-3"].requires = ["pango::pango", "gdk-pixbuf::gdk-pixbuf", "cairo::cairo",
                                                      "fribidi::fribidi", "libepoxy::libepoxy", "glib::glib"]

        self.cpp_info.components["gtk-3"].libs = ["gtk-3"]
        self.cpp_info.components["gtk-3"].set_property("pkg_config_name", "gtk+-3.0")
        self.cpp_info.components["gtk-3"].set_property("pkg_config_custom_content", pkgconfig_vars)
        self.cpp_info.components["gtk-3"].includedirs.append(os.path.join("include", "gtk-3.0"))
        self.cpp_info.components["gtk-3"].requires = ["gdk-3", "pango::pango", "gdk-pixbuf::gdk-pixbuf", "cairo::cairo",
                                                      "fribidi::fribidi", "libepoxy::libepoxy",
                                                      "glib::glib", "at-spi2-core::at-spi2-core"]

        if self.options.get_safe("with_x11", False):
            self.cpp_info.components["gdk-3"].requires.append("xorg::xorg")

            self.cpp_info.components["gdk-x11-3.0"].set_property("pkg_config_name", "gdk-x11-3.0.pc")
            self.cpp_info.components["gdk-x11-3.0"].set_property("pkg_config_custom_content", pkgconfig_vars)
            self.cpp_info.components["gdk-x11-3.0"].includedirs.append(os.path.join("include", "gtk-3.0"))
            self.cpp_info.components["gdk-x11-3.0"].requires = ["gdk-3", "pango::pango", "gdk-pixbuf::gdk-pixbuf", "cairo::cairo",
                                                                "fribidi::fribidi", "libepoxy::libepoxy", "glib::glib"]

            self.cpp_info.components["gtk-x11-3.0"].set_property("pkg_config_name", "gtk+-x11-3.0.pc")
            self.cpp_info.components["gtk-x11-3.0"].set_property("pkg_config_custom_content", pkgconfig_vars)
            self.cpp_info.components["gtk-x11-3.0"].requires = ["gdk-3"]
            self.cpp_info.components["gtk-x11-3.0"].includedirs.append(os.path.join("include", "gtk-3.0"))
            self.cpp_info.components["gtk-x11-3.0"].requires = ["gdk-3", "pango::pango", "gdk-pixbuf::gdk-pixbuf", "cairo::cairo",
                                                                 "fribidi::fribidi", "libepoxy::libepoxy",
                                                                 "glib::glib", "at-spi2-core::at-spi2-core"]

        if self.options.get_safe("with_wayland", False):
            self.cpp_info.components["gdk-3"].requires.extend(["wayland::wayland", "xkbcommon::xkbcommon"])

            self.cpp_info.components["gdk-wayland-3.0"].set_property("pkg_config_name", "gdk-wayland-3.0.pc")
            self.cpp_info.components["gdk-wayland-3.0"].set_property("pkg_config_custom_content", pkgconfig_vars)
            self.cpp_info.components["gdk-wayland-3.0"].requires = ["gdk-3", "pango::pango", "gdk-pixbuf::gdk-pixbuf", "cairo::cairo",
                                                                    "fribidi::fribidi", "libepoxy::libepoxy",
                                                                    "glib::glib", "wayland::wayland", "xkbcommon::xkbcommon"]

            self.cpp_info.components["gtk-wayland-3.0"].set_property("pkg_config_name", "gtk+-wayland-3.0.pc")
            self.cpp_info.components["gtk-wayland-3.0"].set_property("pkg_config_custom_content", pkgconfig_vars)
            self.cpp_info.components["gtk-wayland-3.0"].libs = ["gtk-3"]
            self.cpp_info.components["gtk-wayland-3.0"].includedirs.append(os.path.join("include", "gtk-3.0"))
            self.cpp_info.components["gtk-wayland-3.0"].requires = ["gdk-3", "pango::pango", "gdk-pixbuf::gdk-pixbuf", "cairo::cairo",
                                                                    "fribidi::fribidi", "libepoxy::libepoxy",
                                                                    "glib::glib", "at-spi2-core::at-spi2-core",
                                                                    "wayland::wayland", "xkbcommon::xkbcommon"]
        if self.settings.os == "Macos":
            self.cpp_info.components["gdk-3"].frameworks = ["Cocoa", "Carbon", "CoreGraphics", "CoreVideo", "IOSurface", "QuartzCore"]

            self.cpp_info.components["gdk-quartz-3.0"].set_property("pkg_config_name", "gdk-quartz-3.0.pc")
            self.cpp_info.components["gdk-quartz-3.0"].set_property("pkg_config_custom_content", pkgconfig_vars)
            self.cpp_info.components["gdk-quartz-3.0"].libs = ["gdk-3"]
            self.cpp_info.components["gdk-quartz-3.0"].includedirs.append(os.path.join("include", "gtk-3.0"))
            self.cpp_info.components["gdk-quartz-3.0"].frameworks = ["Cocoa", "Carbon", "CoreGraphics", "CoreVideo",
                                                                     "IOSurface", "QuartzCore"]
            self.cpp_info.components["gdk-quartz-3.0"].requires = ["pango::pango", "gdk-pixbuf::gdk-pixbuf", "cairo::cairo",
                                                                   "fribidi::fribidi", "libepoxy::libepoxy", "glib::glib"]

            self.cpp_info.components["gtk-quartz-3.0"].set_property("pkg_config_name", "gtk+-quartz-3.0.pc")
            self.cpp_info.components["gtk-quartz-3.0"].set_property("pkg_config_custom_content", pkgconfig_vars)
            self.cpp_info.components["gtk-quartz-3.0"].libs = ["gtk-3"]
            self.cpp_info.components["gtk-quartz-3.0"].includedirs.append(os.path.join("include", "gtk-3.0"))
            self.cpp_info.components["gtk-quartz-3.0"].requires = ["gdk-3", "pango::pango", "gdk-pixbuf::gdk-pixbuf", "cairo::cairo",
                                                                    "fribidi::fribidi", "libepoxy::libepoxy", "glib::glib"]
        elif self.settings.os == "Windows":
            windows_system_libs = ["gdi32", "imm32", "shell32", "ole32", "winmm", "dwmapi", "setupapi", "cfgmgr32", "hid", "winspool", "comctl32", "comdlg32"]
            self.cpp_info.components["gdk-3"].system_libs = windows_system_libs

            self.cpp_info.components["gdk-win32-3.0"].set_property("pkg_config_name", "gdk-win32-3.0.pc")
            self.cpp_info.components["gdk-win32-3.0"].set_property("pkg_config_custom_content", pkgconfig_vars)
            self.cpp_info.components["gdk-win32-3.0"].libs = ["gdk-3"]
            self.cpp_info.components["gdk-win32-3.0"].system_libs = windows_system_libs
            self.cpp_info.components["gdk-win32-3.0"].includedirs.append(os.path.join("include", "gtk-3.0"))
            self.cpp_info.components["gdk-win32-3.0"].requires = ["pango::pango", "gdk-pixbuf::gdk-pixbuf", "cairo::cairo",
                                                                  "fribidi::fribidi", "libepoxy::libepoxy", "glib::glib"]

            self.cpp_info.components["gtk-win32-3.0"].set_property("pkg_config_name", "gtk+-win32-3.0")
            self.cpp_info.components["gtk-win32-3.0"].set_property("pkg_config_custom_content", pkgconfig_vars)
            self.cpp_info.components["gtk-win32-3.0"].libs = ["gtk-3"]
            self.cpp_info.components["gtk-win32-3.0"].system_libs = windows_system_libs
            self.cpp_info.components["gtk-win32-3.0"].includedirs.append(os.path.join("include", "gtk-3.0"))
            self.cpp_info.components["gtk-win32-3.0"].requires = ["gdk-3", "pango::pango", "gdk-pixbuf::gdk-pixbuf", "cairo::cairo",
                                                                  "fribidi::fribidi", "libepoxy::libepoxy", "glib::glib"]

        self.cpp_info.components["gail"].libs = ["gailutil-3"]
        self.cpp_info.components["gail"].set_property("pkg_config_name", "gail-3.0")
        self.cpp_info.components["gail"].includedirs.append(os.path.join("include", "gail-3.0"))
        self.cpp_info.components["gail"].requires = ["gtk-3", "at-spi2-core::at-spi2-core"]

        if self.settings.os != "Windows":
            self.cpp_info.components["unix-print"].set_property("pkg_config_name", "gtk+-unix-print-3.0")
            self.cpp_info.components["unix-print"].includedirs.append(os.path.join("include", "gtk-3.0", "unix-print"))
            self.cpp_info.components["unit-print"].requires = ["gtk-3", "at-spi2-core::at-spi2-core", "cairo::cairo",
                                                               "gdk-pixbuf::gdk-pixbuf", "glib::glib"]
