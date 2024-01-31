import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, replace_in_file, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.56.0 <2 || >=2.0.6"


class GtkConan(ConanFile):
    name = "gtk"
    description = "libraries used for creating graphical user interfaces for applications."
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gtk.org"
    topics = "widgets"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_wayland": [True, False],
        "with_x11": [True, False],
        "with_pango": [True, False],
        "with_ffmpeg": [True, False],
        "with_gstreamer": [True, False],
        "with_cups": [True, False],
        "with_cloudprint": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_wayland": False,
        "with_x11": True,
        "with_pango": True,
        "with_ffmpeg": False,
        "with_gstreamer": False,
        "with_cups": False,
        "with_cloudprint": False,
    }

    @property
    def _gtk4(self):
        return Version(self.version).major == 4

    @property
    def _gtk3(self):
        return Version(self.version).major == 3

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            # Fix duplicate definitions of DllMain
            self.options["gdk-pixbuf"].shared = True
            # Fix segmentation fault
            self.options["cairo"].shared = True
        if self._gtk4:
            # The upstream meson file does not create a static library
            # See https://github.com/GNOME/gtk/commit/14f0a0addb9a195bad2f8651f93b95450b186bd6
            self.options.shared = True
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
        if self._gtk4 or not is_msvc(self):
            self.requires("cairo/1.18.0", transitive_headers=True, transitive_libs=True)
        if self._gtk4:
            # INFO: https://gitlab.gnome.org/GNOME/gtk/-/blob/4.10.0/gsk/gsktypes.h#L25
            self.requires("graphene/1.10.8", transitive_headers=True, transitive_libs=True)
            self.requires("fribidi/1.0.13")
            self.requires("libpng/[>=1.6 <2]")
            self.requires("libtiff/4.6.0")
            self.requires("libjpeg/9e")
            if Version(self.version) >= "4.13.2":
                self.requires("libdrm/2.4.120")
        if self.settings.os in ["Linux", "FreeBSD"]:
            if self._gtk4 or self.options.with_wayland:
                self.requires("xkbcommon/1.6.0")
            if self.options.with_wayland:
                self.requires("wayland/1.22.0")
                self.requires("wayland-protocols/1.33")
            if self.options.with_x11:
                # https://gitlab.gnome.org/GNOME/gtk/-/blob/4.10.0/gdk/x11/gdkx11display.h#L35-36
                self.requires("xorg/system", transitive_headers=True, transitive_libs=True)
        if self._gtk3:
            # https://gitlab.gnome.org/GNOME/gtk/-/blob/3.24.37/gtk/gtkwidget.h?ref_type=tags#L36
            self.requires("at-spi2-core/2.51.0", transitive_headers=True, transitive_libs=True)
        self.requires("libepoxy/1.5.10")
        if self.options.with_pango:
            self.requires("pango/1.51.0", transitive_headers=True, transitive_libs=True)
        if self.options.with_ffmpeg:
            self.requires("ffmpeg/6.1")
        if self.options.with_gstreamer:
            self.requires("gstreamer/1.22.6")
        self.requires("fontconfig/2.15.0", override=True)

    def validate(self):
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("this recipes does not support GCC before version 5. contributions are welcome")
        if is_msvc(self):
            if Version(self.version) < "4.2":
                raise ConanInvalidConfiguration("MSVC support of this recipe requires at least gtk/4.2")
            if not self.dependencies["gdk-pixbuf"].options.shared:
                raise ConanInvalidConfiguration("MSVC build requires shared gdk-pixbuf")
            if not self.dependencies["cairo"].options.shared:
                raise ConanInvalidConfiguration("MSVC build requires shared cairo")
        if self._gtk4 and not self.options.shared:
            raise ConanInvalidConfiguration("gtk supports only shared since 4.1.0")

    def build_requirements(self):
        self.tool_requires("meson/1.4.0")
        self.tool_requires("glib/<host_version>")
        if self._gtk4:
            self.tool_requires("libxml2/[>=2.12.5 <3]")  # for xmllint
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.2.0")
        if self._gtk4:
            self.tool_requires("sassc/3.6.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()
        # Required for glib-compile-resources
        VirtualRunEnv(self).generate(scope="build")

        tc = MesonToolchain(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            tc.project_options["wayland_backend" if self._gtk3 else "wayland-backend"] = "true" if self.options.with_wayland else "false"
            tc.project_options["x11_backend" if self._gtk3 else "x11-backend"] = "true" if self.options.with_x11 else "false"
        tc.project_options["introspection"] = "false" if self._gtk3 else "disabled"
        tc.project_options["gtk_doc"] = "false"
        tc.project_options["man-pages" if self._gtk4 else "man"] = "false"
        tc.project_options["tests" if self._gtk3 else "build-tests"] = "false"
        tc.project_options["examples" if self._gtk3 else "build-examples"] = "false"
        tc.project_options["demos"] = "false"
        tc.project_options["datadir"] = os.path.join(self.package_folder, "res", "share")
        tc.project_options["localedir"] = os.path.join(self.package_folder, "res", "share", "locale")
        tc.project_options["sysconfdir"] = os.path.join(self.package_folder, "res", "etc")
        if self._gtk4:
            enabled_disabled = lambda opt: "enabled" if opt else "disabled"
            tc.project_options["media-ffmpeg"] = enabled_disabled(self.options.with_ffmpeg)
            tc.project_options["media-gstreamer"] = enabled_disabled(self.options.with_gstreamer)
            tc.project_options["print-cups"] = enabled_disabled(self.options.with_cups)
        tc.generate()

        tc = PkgConfigDeps(self)
        tc.generate()

    def _patch_sources(self):
        if "4.6.2" <= Version(self.version) < "4.9.2":
            replace_in_file(self, os.path.join(self.source_folder, "meson.build"), "dependency(is_msvc_like ? ", "dependency(false ? ")

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        # args = ["--wrap-mode=nofallback"]
        meson.build()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        meson = Meson(self)
        meson.install()

        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"), recursive=True)
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"), recursive=True)

    def package_info(self):
        if self._gtk3:
            self.cpp_info.components["gdk-3.0"].libs = ["gdk-3"]
            self.cpp_info.components["gdk-3.0"].includedirs = [os.path.join("include", "gtk-3.0")]
            self.cpp_info.components["gdk-3.0"].requires = []
            if self.options.with_pango:
                self.cpp_info.components["gdk-3.0"].requires.extend(["pango::pango_", "pango::pangocairo"])
            self.cpp_info.components["gdk-3.0"].requires.append("gdk-pixbuf::gdk-pixbuf")
            if not is_msvc(self):
                self.cpp_info.components["gdk-3.0"].requires.extend(["cairo::cairo", "cairo::cairo-gobject"])
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["gdk-3.0"].requires.extend(["glib::gio-unix-2.0", "cairo::cairo-xlib"])
                if self.options.with_x11:
                    self.cpp_info.components["gdk-3.0"].requires.append("xorg::xorg")
            self.cpp_info.components["gdk-3.0"].requires.append("libepoxy::libepoxy")
            self.cpp_info.components["gdk-3.0"].set_property("pkg_config_name", "gdk-3.0")

            self.cpp_info.components["gtk+-3.0"].libs = ["gtk-3"]
            self.cpp_info.components["gtk+-3.0"].requires = ["gdk-3.0", "at-spi2-core::at-spi2-core"]
            if not is_msvc(self):
                self.cpp_info.components["gtk+-3.0"].requires.extend(["cairo::cairo", "cairo::cairo-gobject"])
            self.cpp_info.components["gtk+-3.0"].requires.extend(["gdk-pixbuf::gdk-pixbuf", "glib::gio-2.0"])
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["gtk+-3.0"].requires.append("at-spi2-core::at-spi2-core")
            self.cpp_info.components["gtk+-3.0"].requires.append("libepoxy::libepoxy")
            if self.options.with_pango:
                self.cpp_info.components["gtk+-3.0"].requires.append("pango::pangoft2")
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["gtk+-3.0"].requires.append("glib::gio-unix-2.0")
            self.cpp_info.components["gtk+-3.0"].includedirs = [os.path.join("include", "gtk-3.0")]
            self.cpp_info.components["gtk+-3.0"].set_property("pkg_config_name", "gtk+-3.0")

            self.cpp_info.components["gail-3.0"].libs = ["gailutil-3"]
            self.cpp_info.components["gail-3.0"].requires = ["gtk+-3.0", "at-spi2-core::at-spi2-core"]
            self.cpp_info.components["gail-3.0"].includedirs = [os.path.join("include", "gail-3.0")]
            self.cpp_info.components["gail-3.0"].set_property("pkg_config_name", "gail-3.0")
        elif self._gtk4:
            self.cpp_info.set_property("pkg_config_name", "gtk4")
            self.cpp_info.libs = ["gtk-4"]
            self.cpp_info.includedirs.append(os.path.join("include", "gtk-4.0"))
