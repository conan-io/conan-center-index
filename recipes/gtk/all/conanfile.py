from conans import ConanFile, Meson, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class GtkConan(ConanFile):
    name = "gtk"
    description = "libraries used for creating graphical user interfaces for applications."
    topics = ("gtk", "widgets")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gtk.org"
    license = "LGPL-2.1-or-later"
    generators = "pkg_config"

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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _gtk4(self):
        return tools.Version("4.0.0") <= tools.Version(self.version) < tools.Version("5.0.0")
    @property

    def _gtk3(self):
        return tools.Version("3.0.0") <= tools.Version(self.version) < tools.Version("4.0.0")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.with_wayland
            del self.options.with_x11

    def validate(self):
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("this recipes does not support GCC before version 5. contributions are welcome")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os == "Linux":
            if self.options.with_wayland or self.options.with_x11:
                if not self.options.with_pango:
                    raise ConanInvalidConfiguration("with_pango option is mandatory when with_wayland or with_x11 is used")
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("GTK recipe is not yet compatible with Windows. Contributions are welcome.")

    def build_requirements(self):
        self.build_requires("meson/0.59.1")
        self.build_requires("pkgconf/1.7.4")
        if self._gtk4:
            self.build_requires("sassc/3.6.2")

    def requirements(self):
        self.requires("gdk-pixbuf/2.42.4")
        self.requires("glib/2.69.3")
        if self.settings.compiler != "Visual Studio":
            self.requires("cairo/1.17.4")
        if self._gtk4:
            self.requires("graphene/1.10.6")
        if self.settings.os == "Linux":
            if self._gtk4:
                self.requires("xkbcommon/1.3.1")
            if self._gtk3:
                self.requires("at-spi2-atk/2.38.0")
            if self.options.with_wayland:
                if self._gtk3:
                    self.requires("xkbcommon/1.3.1")
                self.requires("wayland/1.19.0")
            if self.options.with_x11:
                self.requires("xorg/system")
        if self._gtk3:
            self.requires("atk/2.36.0")
        self.requires("libepoxy/1.5.9")
        if self.options.with_pango:
            self.requires("pango/1.49.1")
        if self.options.with_ffmpeg:
            self.requires("ffmpeg/4.2.1")
        if self.options.with_gstreamer:
            self.requires("gstreamer/1.19.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_meson(self):
        meson = Meson(self)
        defs = {}
        if self.settings.os == "Linux":
            defs["wayland_backend" if self._gtk3 else "wayland-backend"] = "true" if self.options.with_wayland else "false"
            defs["x11_backend" if self._gtk3 else "x11-backend"] = "true" if self.options.with_x11 else "false"
        defs["introspection"] = "false" if self._gtk3 else "disabled"
        defs["documentation"] = "false"
        defs["man-pages"] = "false"
        defs["tests" if self._gtk3 else "build-tests"] = "false"
        defs["examples" if self._gtk3 else "build-examples"] = "false"
        defs["demos"] = "false"
        defs["datadir"] = os.path.join(self.package_folder, "res", "share")
        defs["localedir"] = os.path.join(self.package_folder, "res", "share", "locale")
        defs["sysconfdir"] = os.path.join(self.package_folder, "res", "etc")
        
        if self._gtk4:
            enabled_disabled = lambda opt : "enabled" if opt else "disabled" 
            defs["media-ffmpeg"] = enabled_disabled(self.options.with_ffmpeg)
            defs["media-gstreamer"] = enabled_disabled(self.options.with_gstreamer)
            defs["print-cups"] = enabled_disabled(self.options.with_cups)
            defs["print-cloudprint"] = enabled_disabled(self.options.with_cloudprint)
        args=[]
        args.append("--wrap-mode=nofallback")
        meson.configure(defs=defs, build_folder=self._build_subfolder, source_folder=self._source_subfolder, pkg_config_paths=[self.install_folder], args=args)
        return meson

    def build(self):
        if self._gtk3:
            tools.replace_in_file(os.path.join(self._source_subfolder, "meson.build"), "\ntest(\n", "\nfalse and test(\n")
        if tools.Version(self.version) >= "4.2.0":
            tools.replace_in_file(os.path.join(self._source_subfolder, "meson.build"),
                                  "gtk_update_icon_cache: true",
                                  "gtk_update_icon_cache: false")
        with tools.environment_append(tools.RunEnvironment(self).vars):
            meson = self._configure_meson()
            meson.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        meson = self._configure_meson()
        with tools.environment_append({
            "PKG_CONFIG_PATH": self.install_folder,
            "PATH": [os.path.join(self.package_folder, "bin")]}):
            meson.install()

        self.copy(pattern="COPYING", src=self._source_subfolder, dst="licenses")
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

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
            self.cpp_info.components["gdk-3.0"].names["pkg_config"] = "gdk-3.0"

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
            self.cpp_info.components["gtk+-3.0"].names["pkg_config"] = "gtk+-3.0"

            self.cpp_info.components["gail-3.0"].libs = ["gailutil-3"]
            self.cpp_info.components["gail-3.0"].requires = ["gtk+-3.0", "atk::atk"]
            self.cpp_info.components["gail-3.0"].includedirs = [os.path.join("include", "gail-3.0")]
            self.cpp_info.components["gail-3.0"].names["pkg_config"] = "gail-3.0"
        elif self._gtk4:
            self.cpp_info.names["pkg_config"] = "gtk4"
            self.cpp_info.libs = ["gtk-4"]
            self.cpp_info.includedirs.append(os.path.join("include", "gtk-4.0"))
