import os

from conan import ConanFile
from conan.tools.meson import MesonToolchain, Meson
from conan.errors import ConanInvalidConfiguration
from conan.tools.scm import Version
from conan.tools.files import get, copy, rm, rmdir, replace_in_file, export_conandata_patches, apply_conandata_patches
from conan.tools.microsoft import is_msvc
from conan.tools.env import VirtualBuildEnv
from conan.tools.gnu import PkgConfigDeps

required_conan_version = ">=1.55.0"


class GtkConan(ConanFile):
    name = "gtk"
    description = "libraries used for creating graphical user interfaces for applications."
    package_type = "library"
    topics = ("gui", "widget", "graphical")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gtk.org"
    license = "LGPL-2.1-or-later"

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
        "with_cloudprint": [True, False]
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
        "with_cloudprint": False
    }

    short_paths = True

    @property
    def _gtk4(self):
        return Version("4.0.0") <= Version(self.version) < Version("5.0.0")

    @property
    def _gtk3(self):
        return Version("3.0.0") <= Version(self.version) < Version("4.0.0")

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            # Fix duplicate definitions of DllMain
            self.options["gdk-pixbuf"].shared = True
            # Fix segmentation fault
            self.options["cairo"].shared = True
        if Version(self.version) >= "4.1.0":
            # The upstream meson file does not create a static library
            # See https://github.com/GNOME/gtk/commit/14f0a0addb9a195bad2f8651f93b95450b186bd6
            self.options.shared = True
        if self.settings.os != "Linux":
            del self.options.with_wayland
            del self.options.with_x11

    def configure(self):
        if self.options.shared:
            self.settings.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("meson/1.0.0")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/1.9.3")
        if self._gtk4:
            self.tool_requires("libxml2/2.10.2")  # for xmllint
        if self._gtk4:
            self.tool_requires("sassc/3.6.2")

    def requirements(self):
        self.requires("pcre2/10.42", override=True)
        self.requires("glib/2.75.2", override=True)

        self.requires("gdk-pixbuf/2.42.10")
        # self.requires("glib/2.75.0")
        if self._gtk4 or not is_msvc(self):
            self.requires("cairo/1.17.4")
        if self._gtk4:
            self.requires("graphene/1.10.8")
            self.requires("fribidi/1.0.12")
            self.requires("libpng/1.6.39")
            self.requires("libtiff/4.4.0")
            self.requires("libjpeg/9e")
        if self.settings.os == "Linux":
            if self._gtk4:
                self.requires("xkbcommon/1.4.1")
            if self._gtk3:
                self.requires("at-spi2-atk/2.38.0")
            if self.options.with_wayland:
                if self._gtk3:
                    self.requires("xkbcommon/1.4.1")
                self.requires("wayland/1.20.0")
            if self.options.with_x11:
                self.requires("xorg/system")
        if self._gtk3:
            self.requires("atk/2.38.0")
        self.requires("libepoxy/1.5.10")
        if self.options.with_pango:
            self.requires("pango/1.50.7")
        if self.options.with_ffmpeg:
            self.requires("ffmpeg/5.0")
        if self.options.with_gstreamer:
            self.requires("gstreamer/1.19.2")

    def validate(self):
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("this recipes does not support GCC before version 5. contributions are welcome")
        if is_msvc(self):
            if Version(self.version) < "4.2":
                raise ConanInvalidConfiguration("MSVC support of this recipe requires at least gtk/4.2")
            if not self.options["gdk-pixbuf"].shared:
                raise ConanInvalidConfiguration("MSVC build requires shared gdk-pixbuf")
            if not self.options["cairo"].shared:
                raise ConanInvalidConfiguration("MSVC build requires shared cairo")
        if Version(self.version) >= "4.1.0":
            if not self.options.shared:
                raise ConanInvalidConfiguration("gtk supports only shared since 4.1.0")
        if self.settings.os == "Linux":
            if self.options.with_wayland or self.options.with_x11:
                if not self.options.with_pango:
                    raise ConanInvalidConfiguration("with_pango option is mandatory when with_wayland or with_x11 is used")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = MesonToolchain(self)

        if self.settings.os == "Linux":
            tc.project_options["wayland_backend" if self._gtk3 else "wayland-backend"] = "true" if self.options.with_wayland else "false"
            tc.project_options["x11_backend" if self._gtk3 else "x11-backend"] = "true" if self.options.with_x11 else "false"
        tc.project_options["introspection"] = "false" if self._gtk3 else "disabled"
        tc.project_options["gtk_doc"] = "false"
        tc.project_options["man-pages" if self._gtk4 else "man"] = "false"
        tc.project_options["tests" if self._gtk3 else "build-tests"] = "false"
        tc.project_options["examples" if self._gtk3 else "build-examples"] = "false"
        tc.project_options["demos"] = "false"
        tc.project_options["datadir"] = os.path.join("res", "share")
        tc.project_options["localedir"] = os.path.join("res", "share", "locale")
        tc.project_options["sysconfdir"] = os.path.join("res", "etc")

        if self._gtk4:
            def enabled_disabled(opt): return "enabled" if opt else "disabled"
            tc.project_options["media-ffmpeg"] = enabled_disabled(self.options.with_ffmpeg)
            tc.project_options["media-gstreamer"] = enabled_disabled(self.options.with_gstreamer)
            tc.project_options["print-cups"] = enabled_disabled(self.options.with_cups)
            if Version(self.version) < "4.3.2":
                tc.project_options["print-cloudprint"] = enabled_disabled(self.options.with_cloudprint)

        tc.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if self._gtk3:
            replace_in_file(self, os.path.join(self.source_folder, "meson.build"),
                            "\ntest(\n",
                            "\nfalse and test(\n")
        if "4.2.0" <= Version(self.version) < "4.6.1":
            replace_in_file(self, os.path.join(self.source_folder, "meson.build"),
                            "gtk_update_icon_cache: true",
                            "gtk_update_icon_cache: false")
        if "4.6.2" <= Version(self.version):
            replace_in_file(self, os.path.join(self.source_folder, "meson.build"),
                            "dependency(is_msvc_like ? ",
                            "dependency(false ? ")

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst="licenses")
        copy(self, pattern="COPYING", src=self.source_folder, dst="licenses")
        meson = Meson(self)
        meson.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, pattern="*.pdb", folder=os.path.join(self.package_folder, "bin"))
        rm(self, pattern="*.pdb", folder=os.path.join(self.package_folder, "lib"))

    def package_info(self):
        if self._gtk3:
            self.cpp_info.components["gdk-3.0"].libs = ["gdk-3"]
            self.cpp_info.components["gdk-3.0"].includedirs = [os.path.join("include", "gtk-3.0")]
            self.cpp_info.components["gdk-3.0"].requires = []
            if self.options.with_pango:
                self.cpp_info.components["gdk-3.0"].requires.extend(["pango::pango_", "pango::pangocairo"])
            self.cpp_info.components["gdk-3.0"].requires.append("gdk-pixbuf::gdk-pixbuf")
            if self.settings.compiler != "Visual Studio":
                self.cpp_info.components["gdk-3.0"].requires.extend(["cairo::cairo", "cairo::cairo-gobject"])
            if self.settings.os == "Linux":
                self.cpp_info.components["gdk-3.0"].requires.extend(["glib::gio-unix-2.0", "cairo::cairo-xlib"])
                if self.options.with_x11:
                    self.cpp_info.components["gdk-3.0"].requires.append("xorg::xorg")
            self.cpp_info.components["gdk-3.0"].requires.append("libepoxy::libepoxy")
            self.cpp_info.components["gdk-3.0"].set_property("pkg_config_name", "gdk-3.0")

            self.cpp_info.components["gtk+-3.0"].libs = ["gtk-3"]
            self.cpp_info.components["gtk+-3.0"].requires = ["gdk-3.0", "atk::atk"]
            if self.settings.compiler != "Visual Studio":
                self.cpp_info.components["gtk+-3.0"].requires.extend(["cairo::cairo", "cairo::cairo-gobject"])
            self.cpp_info.components["gtk+-3.0"].requires.extend(["gdk-pixbuf::gdk-pixbuf", "glib::gio-2.0"])
            if self.settings.os == "Linux":
                self.cpp_info.components["gtk+-3.0"].requires.append("at-spi2-atk::at-spi2-atk")
            self.cpp_info.components["gtk+-3.0"].requires.append("libepoxy::libepoxy")
            if self.options.with_pango:
                self.cpp_info.components["gtk+-3.0"].requires.append('pango::pangoft2')
            if self.settings.os == "Linux":
                self.cpp_info.components["gtk+-3.0"].requires.append("glib::gio-unix-2.0")
            self.cpp_info.components["gtk+-3.0"].includedirs = [os.path.join("include", "gtk-3.0")]
            self.cpp_info.components["gtk+-3.0"].set_property("pkg_config_name", "gtk+-3.0")

            self.cpp_info.components["gail-3.0"].libs = ["gailutil-3"]
            self.cpp_info.components["gail-3.0"].requires = ["gtk+-3.0", "atk::atk"]
            self.cpp_info.components["gail-3.0"].includedirs = [os.path.join("include", "gail-3.0")]
            self.cpp_info.components["gail-3.0"].set_property("pkg_config_name", "gail-3.0")
        elif self._gtk4:
            self.cpp_info.set_property("pkg_config_name", "gtk4")
            self.cpp_info.libs = ["gtk-4"]
            self.cpp_info.includedirs.append(os.path.join("include", "gtk-4.0"))
