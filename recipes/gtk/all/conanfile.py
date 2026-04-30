from conan import ConanFile
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.gnu import PkgConfigDeps
from conan.tools.files import get, copy, rmdir
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
    package_type = "shared-library"
    languages = "C"
    settings = "os", "arch", "compiler", "build_type"
    implements = ["auto_shared_fpic"]
    options = {
        "with_wayland": [True, False],
        "with_x11": [True, False],
    }
    default_options = {
        "with_wayland": False,
        "with_x11": True,
    }

    def config_options(self):
        if self.settings.os != "Linux":
            del self.options.with_wayland
            del self.options.with_x11

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        # INFO: GTK requires glib-compile-resources
        self.tool_requires("glib/<host_version>")
        if self.options.get_safe("with_wayland", False):
            self.tool_requires("wayland/<host_version>")
            self.tool_requires("wayland-protocols/[>=1.42 <2]")

    def requirements(self):
        # INFO: gtkconfig.h:8 glib.h
        self.requires("glib/[>=2.82 <3]", transitive_headers=True)
        # INFO: gdktexture.h:26 gdk-pixbuf.h/gdk-pixbuf.h
        self.requires("gdk-pixbuf/[>=2.42 <3]", transitive_headers=True)
        # INFO: gdktypes.h:36 cairo.h
        self.requires("cairo/[>=1.18 <2]", transitive_headers=True)
        # INFO: gtkscrollinfo.h:29 graphene.h
        self.requires("graphene/1.10.8", transitive_headers=True)
        # INFO: gdkcairo.h:26 pango/pangocairo.h
        self.requires("pango/[>=1.50.7 <2]", transitive_headers=True)
        # TODO: Consider to depend on libjpeg-turbo
        self.requires("libjpeg/[>=9f]")
        self.requires("fribidi/1.0.13")
        self.requires("libpng/[>=1.6 <2]")
        self.requires("libtiff/[>=4.6.0 <5]")
        self.requires("libepoxy/1.5.10")
        if self.settings.os == "Linux":
            if self.options.with_wayland:
                self.requires("xkbcommon/[>=1.5.0 <2]")
                self.requires("wayland/[>=1.23 <2]")
            if self.options.with_x11:
                self.requires("xorg/system")
            self.requires("libdrm/[>=2.4 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        # GDK backends
        tc.project_options["wayland-backend"] = "true" if self.options.get_safe("with_wayland", False) else "false"
        tc.project_options["x11-backend"] = "true" if self.options.get_safe("with_x11", False) else "false"
        tc.project_options["win32-backend"] = self.settings.os == "Windows"
        tc.project_options["macos-backend"] = self.settings.os == "Macos"
        tc.project_options["android-backend"] = self.settings.os == "Android"
        tc.project_options["broadway-backend"] = "false"
        # Media backends
        tc.project_options["media-gstreamer"] = "disabled"
        # Print backends
        tc.project_options["print-cups"] = "disabled"
        tc.project_options["print-cpdb"] = "disabled"
        # Optional features
        tc.project_options["vulkan"] = "disabled"
        tc.project_options["cloudproviders"] = "disabled"
        tc.project_options["sysprof"] = "disabled"
        tc.project_options["tracker"] = "disabled"
        tc.project_options["colord"] = "disabled"
        tc.project_options["f16c"] = "disabled"
        tc.project_options["accesskit"] = "disabled"
        # Introspection
        tc.project_options["introspection"] = "disabled"
        # Documentation
        tc.project_options["documentation"] = "false"
        tc.project_options["screenshots"] = "false"
        tc.project_options["man-pages"] = "false"
        # Demos, examples and tests
        tc.project_options["profile"] = "devel"
        tc.project_options["build-demos"] = "false"
        tc.project_options["build-testsuite"] = "false"
        tc.project_options["build-examples"] = "false"
        tc.project_options["build-tests"] = "false"
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

        # INFO: wayland-scanner needs to load wayland shared library at runtime
        # Meson wayland.wlmod.find_protocol uses pkg-config to find wayland-scanner.pc file
        # Adjust pkg_config_custom_content to point to build context binary directory
        if self.options.get_safe("with_wayland", False):
            wayland_scanner_config_vars = self.dependencies.host['wayland'].cpp_info.components['wayland-scanner'].get_property("pkg_config_custom_content", None)
            if wayland_scanner_config_vars:
                wayland_build_context_bindir = self.dependencies.build['wayland'].cpp_info.bindirs[0]
                wayland_scanner_config_vars = wayland_scanner_config_vars.replace("${bindir}", wayland_build_context_bindir)
                deps.set_property("wayland::wayland-scanner", "pkg_config_custom_content", wayland_scanner_config_vars)
            deps.generate()

    def validate(self):
        if self.settings.os == "Linux" and not (self.options.with_wayland or self.options.with_x11):
            raise ConanInvalidConfiguration("At least one of backends '-o &:with_wayland' or '-o &:with_x11' options must be True on Linux")

        # INFO: Avoid embedding static dependencies into shared library
        for req, dep in self.dependencies.direct_host.items():
            if dep.options.get_safe("shared", None) == False and dep.options.get_safe("header_only", False) == False:
                raise ConanInvalidConfiguration(f"{req.ref} is static; {self.name} requires '-o \"*/*:shared=True\"' to be built as shared library")

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

    def package_info(self):
        gtk_targets = []
        if self.options.get_safe("with_x11", False):
            gtk_targets.append("x11")
        if self.options.get_safe("with_wayland", False):
            gtk_targets.append("wayland")
        if self.settings.os == "Windows":
            gtk_targets.append("win32")
        if self.settings.os == "Macos":
            gtk_targets.append("macos")
        pkgconfig_vars = {
            "targets": gtk_targets,
            "gtk_binary_version": f"{Version(self.version).major}.0.0",
            "gtk_host": f"{self.settings.arch}-" + str(self.settings.os).lower()
        }

        self.cpp_info.components["gtk-4"].libs = ["gtk-4"]
        self.cpp_info.components["gtk-4"].set_property("pkg_config_name", "gtk4")
        self.cpp_info.components["gtk-4"].set_property("pkg_config_custom_content", pkgconfig_vars)
        self.cpp_info.components["gtk-4"].includedirs.append(os.path.join("include", "gtk-4.0"))
        self.cpp_info.components["gtk-4"].requires = ["pango::pango", "gdk-pixbuf::gdk-pixbuf", "cairo::cairo",
                                                      "fribidi::fribidi", "libepoxy::libepoxy", "libtiff::libtiff",
                                                      "libjpeg::libjpeg", "libpng::libpng", "glib::glib", "graphene::graphene"]
        if self.settings.os == "Linux":
            self.cpp_info.components["gtk-4"].requires.extend(["libdrm::libdrm"])
            self.cpp_info.components["gtk-4"].system_libs = ["m"]

            self.cpp_info.components["gtk-unix-print"].set_property("pkg_config_name", "gtk4-unix-print")
            self.cpp_info.components["gtk-unix-print"].set_property("pkg_config_custom_content", pkgconfig_vars)
            self.cpp_info.components["gtk-unix-print"].libdirs = []
            self.cpp_info.components["gtk-unix-print"].includedirs.append(os.path.join("include", "gtk-4.0", "unix-print"))
            self.cpp_info.components["gtk-unix-print"].requires = ["gtk-4"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["gtk-win32"].set_property("pkg_config_name", "gtk4-win32")
            self.cpp_info.components["gtk-win32"].set_property("pkg_config_custom_content", pkgconfig_vars)
            self.cpp_info.components["gtk-win32"].libdirs = []
            self.cpp_info.components["gtk-win32"].requires = ["gtk-4"]
        elif self.settings.os == "Macos":
            self.cpp_info.components["gtk-macos"].set_property("pkg_config_name", "gtk4-macos")
            self.cpp_info.components["gtk-macos"].set_property("pkg_config_custom_content", pkgconfig_vars)
            self.cpp_info.components["gtk-macos"].libdirs = []
            self.cpp_info.components["gtk-macos"].requires = ["gtk-4"]

        if self.options.get_safe("with_x11", False):
            self.cpp_info.components["gtk-x11"].set_property("pkg_config_name", "gtk4-x11")
            self.cpp_info.components["gtk-x11"].set_property("pkg_config_custom_content", pkgconfig_vars)
            self.cpp_info.components["gtk-x11"].libdirs = []
            self.cpp_info.components["gtk-x11"].requires = ["gtk-4", "xorg::xorg"]

        if self.options.get_safe("with_wayland", False):
            self.cpp_info.components["gtk-wayland"].set_property("pkg_config_name", "gtk4-wayland")
            self.cpp_info.components["gtk-wayland"].set_property("pkg_config_custom_content", pkgconfig_vars)
            self.cpp_info.components["gtk-wayland"].libdirs = []
            self.cpp_info.components["gtk-wayland"].requires = ["gtk-4", "wayland::wayland", "xkbcommon::xkbcommon"]