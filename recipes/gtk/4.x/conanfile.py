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
        "with_wayland": [True, False],
        "with_x11": [True, False],
        "with_cups": [True, False],
        "with_gstreamer": [True, False],
    }
    default_options = {
        "with_wayland": True,
        "with_x11": True,
        "with_cups": False,
        "with_gstreamer": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            # Fix duplicate definitions of DllMain
            self.options["gdk-pixbuf"].shared = True
            # Fix segmentation fault
            self.options["cairo"].shared = True
        if self.settings.os not in ["Linux", "FreeBSD"]:
            self.options.rm_safe("with_wayland")
            self.options.rm_safe("with_x11")

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # INFO: https://gitlab.gnome.org/GNOME/gtk/-/blob/4.10.0/gdk/gdktypes.h?ref_type=tags#L34-38
        self.requires("glib/2.78.3", transitive_headers=True, transitive_libs=True)
        # INFO: https://gitlab.gnome.org/GNOME/gtk/-/blob/4.10.0/gdk/gdkpixbuf.h?ref_type=tags#L32-33
        # Note: gdkpixbuf.h is deprecated in newer versions
        self.requires("gdk-pixbuf/2.42.10", transitive_headers=True, transitive_libs=True)
        self.requires("pango/1.51.0", transitive_headers=True, transitive_libs=True)
        self.requires("cairo/1.18.0", transitive_headers=True, transitive_libs=True)
        # INFO: https://gitlab.gnome.org/GNOME/gtk/-/blob/4.10.0/gsk/gsktypes.h#L25
        self.requires("graphene/1.10.8", transitive_headers=True, transitive_libs=True)
        self.requires("libepoxy/1.5.10")
        self.requires("fribidi/1.0.13")
        self.requires("libpng/[>=1.6 <2]")
        self.requires("libtiff/4.6.0")
        self.requires("libjpeg/9e")
        if Version(self.version) >= "4.13.2":
            self.requires("libdrm/2.4.120")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("xkbcommon/1.6.0")
            if self.options.with_wayland:
                self.requires("wayland/1.22.0")
                self.requires("wayland-protocols/1.33")
            if self.options.with_x11:
                # https://gitlab.gnome.org/GNOME/gtk/-/blob/4.10.0/gdk/x11/gdkx11display.h#L35-36
                self.requires("xorg/system", transitive_headers=True, transitive_libs=True)
        if self.options.with_gstreamer:
            self.requires("gstreamer/1.24.7")

    def validate(self):
        if is_msvc(self):
            if not self.dependencies["gdk-pixbuf"].options.shared:
                raise ConanInvalidConfiguration("MSVC build requires shared gdk-pixbuf")
            if not self.dependencies["cairo"].options.shared:
                raise ConanInvalidConfiguration("MSVC build requires shared cairo")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        self.tool_requires("glib/<host_version>")
        self.tool_requires("libxml2/[>=2.12.5 <3]")  # for xmllint
        self.tool_requires("sassc/3.6.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()
        # Required for glib-compile-resources
        VirtualRunEnv(self).generate(scope="build")

        enabled_disabled = lambda opt: "enabled" if opt else "disabled"
        tc = MesonToolchain(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            tc.project_options["wayland-backend"] = "true" if self.options.with_wayland else "false"
            tc.project_options["x11-backend"] = "true" if self.options.with_x11 else "false"
        tc.project_options["introspection"] = "disabled"
        tc.project_options["documentation"] = "false"
        tc.project_options["screenshots"] = "false"
        tc.project_options["man-pages"] = "false"
        tc.project_options["build-tests"] = "false"
        tc.project_options["build-testsuite"] = "false"
        tc.project_options["build-demos"] = "false"
        tc.project_options["build-examples"] = "false"
        tc.project_options["datadir"] = os.path.join("res", "share")
        tc.project_options["localedir"] = os.path.join("res", "share", "locale")
        tc.project_options["sysconfdir"] = os.path.join("res", "etc")
        tc.project_options["media-gstreamer"] = enabled_disabled(self.options.with_gstreamer)
        tc.project_options["print-cups"] = enabled_disabled(self.options.with_cups)
        tc.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

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
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"), recursive=True)
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"), recursive=True)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "gtk4")
        self.cpp_info.libs = ["gtk-4"]
        self.cpp_info.includedirs.append(os.path.join("include", "gtk-4.0"))
