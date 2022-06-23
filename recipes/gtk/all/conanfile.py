from conans import ConanFile, Meson, tools
from conans.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc
import os
import fileinput
import shlex

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
        "with_ffmpeg": False,
        "with_gstreamer": False,
        "with_cups": False,
        "with_cloudprint": False
    }

    short_paths = True

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

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if tools.Version(self.version) >= "4.1.0":
            # The upstream meson file does not create a static library
            # See https://github.com/GNOME/gtk/commit/14f0a0addb9a195bad2f8651f93b95450b186bd6
            self.options.shared = True
        if self.settings.os != "Linux":
            del self.options.with_wayland
            del self.options.with_x11

    def validate(self):
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("this recipes does not support GCC before version 5. contributions are welcome")
        if is_msvc(self):
            # TODO: Remove once gtk 4.1.2 and 4.0.2 are removed
            if self._gtk4 and tools.Version(self.version) < "4.2":
                raise ConanInvalidConfiguration("MSVC support of this recipe requires at least gtk/4.2")
            # TODO: Remove once gtk 3.24.24 is removed
            if self._gtk3 and tools.Version(self.version) < "3.24.34":
                raise ConanInvalidConfiguration("MSVC support of this recipe requires at least gtk/3.24.34")
        if tools.Version(self.version) >= "4.1.0":
            if not self.options.shared:
                raise ConanInvalidConfiguration("gtk supports only shared since 4.1.0")
        if self.settings.os == "Linux" and (self.options.with_wayland or self.options.with_x11) and not self.options["pango"].with_freetype:
            raise ConanInvalidConfiguration(
                "gtk requires pango with freetype when built with wayland/x11 support")
        if self.settings.compiler == "clang":
            # FIXME: gdk-pixbuf cannot be built using clang with the latest glib
            # which all other dependencies of gtk depend on
            # see https://github.com/conan-io/conan-center-index/pull/10154#issuecomment-1094224794
            raise ConanInvalidConfiguration(
                "this recipe does not support building with clang")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            self.options["glib"].shared = True
            self.options["cairo"].shared = True
            self.options["pango"].shared = True
            self.options["gdk-pixbuf"].shared = True
            if self._gtk3:
                self.options["atk"].shared = True
                if self.settings.os == "Linux" and self.options.with_x11:
                    self.options["at-spi2-atk"].shared = True
            if self._gtk4:
                self.options["graphene"].shared = True

    def build_requirements(self):
        self.build_requires("meson/0.62.2")
        if self._gtk4:
            self.build_requires("libxml2/2.9.14") # for xmllint
        self.build_requires("pkgconf/1.7.4")
        if self._gtk4:
            self.build_requires("sassc/3.6.2")

    def requirements(self):
        self.requires("gdk-pixbuf/2.42.8")
        self.requires("glib/2.73.0")
        if self._gtk4 or self.settings.compiler != "Visual Studio":
            self.requires("cairo/1.17.4")
        if self._gtk4:
            self.requires("graphene/1.10.8")
            self.requires("fribidi/1.0.12")
            self.requires("libpng/1.6.37")
            self.requires("libtiff/4.3.0")
            self.requires("libjpeg/9d")
        if self.settings.os == "Linux":
            if self.options.with_wayland:
                self.requires("xkbcommon/1.4.1")
                self.requires("wayland/1.20.0")
            if self.options.with_x11:
                self.requires("xorg/system")
                if self._gtk3:
                    self.requires("at-spi2-atk/2.38.0")
        if self._gtk3:
            self.requires("atk/2.38.0")
        self.requires("libepoxy/1.5.10")
        self.requires("pango/1.50.7")
        if self.options.with_ffmpeg:
            self.requires("ffmpeg/5.0")
        if self.options.with_gstreamer:
            self.requires("gstreamer/1.19.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_meson(self):
        meson = Meson(self)
        defs = {}
        if self.settings.os == "Linux":
            defs["wayland_backend" if self._gtk3 else "wayland-backend"] = "true" if self.options.with_wayland else "false"
            defs["x11_backend" if self._gtk3 else "x11-backend"] = "true" if self.options.with_x11 else "false"
        defs["introspection"] = "false" if self._gtk3 else "disabled"
        defs["gtk_doc"] = "false"
        defs["man-pages" if self._gtk4 else "man"] = "false"
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
            if tools.Version(self.version) < "4.3.2":
                defs["print-cloudprint"] = enabled_disabled(self.options.with_cloudprint)
        args=[]
        args.append("--wrap-mode=nofallback")
        meson.configure(defs=defs, build_folder=self._build_subfolder, source_folder=self._source_subfolder, pkg_config_paths=[self.install_folder], args=args)
        return meson

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if self._gtk3:
            tools.replace_in_file(os.path.join(self._source_subfolder, "meson.build"), "\ntest(\n", "\nfalse and test(\n")
        if "4.2.0" <= tools.Version(self.version) < "4.6.1":
            tools.replace_in_file(os.path.join(self._source_subfolder, "meson.build"),
                                  "gtk_update_icon_cache: true",
                                  "gtk_update_icon_cache: false")
        if "4.6.2" <= tools.Version(self.version):
            tools.replace_in_file(os.path.join(self._source_subfolder, "meson.build"),
                                  "dependency(is_msvc_like ? ",
                                  "dependency(false ? ")
        with tools.environment_append(tools.RunEnvironment(self).vars):
            meson = self._configure_meson()

            cwd = os.path.join(os.getcwd(), self._build_subfolder).replace("\\", "/")
            for line in fileinput.input(os.path.join(self._build_subfolder, "build.ninja"), inplace=True):
                # the command response file for linking gtk exceeds msvc linker limit
                # this hack fixes this by removing duplicates in the link arguments
                # inside the build.ninja file
                # see https://docs.microsoft.com/en-us/cpp/error-messages/tool-errors/linker-tools-error-lnk1170?view=msvc-170
                idx = line.find("LINK_ARGS =")
                if idx >= 0:
                    parts = shlex.split(line[idx + len("LINK_ARGS ="):])
                    print("{} {}".format(
                        line[: idx + len("LINK_ARGS =")],
                        " ".join((f'"{v}"' for v in dict.fromkeys(parts)))), end='')
                    continue

                # in windows, ninja uses CreateProcess which has a limit of 32767 chars
                # gnome.mkenums uses absolute paths, which increases the command length
                # see: https://github.com/mesonbuild/meson/issues/6710
                # this hack replaces all absolute paths of the build subfolder
                # with relative paths to decrease the length of the command
                idx = line.find("COMMAND = ")
                if idx >= 0:
                    parts = shlex.split(line[idx + len("COMMAND ="):])
                    print("{} {}".format(
                        line[: idx + len("COMMAND =")],
                        " ".join((f'"{v.replace(cwd, ".")}"' for v in parts))))
                    continue

                print(line, end='')

            meson.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        meson = self._configure_meson()
        with tools.environment_append({**tools.RunEnvironment(self).vars,
                                       "PKG_CONFIG_PATH": self.install_folder}):
            meson.install()

        self.copy(pattern="COPYING", src=self._source_subfolder, dst="licenses")
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.pdb")
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.pdb")

    def package_info(self):
        if self._gtk3:
            self.cpp_info.components["gdk-3.0"].libs = ["gdk-3"]
            self.cpp_info.components["gdk-3.0"].includedirs = [os.path.join("include", "gtk-3.0")]
            self.cpp_info.components["gdk-3.0"].requires = []
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
            if (self.settings.os == "Linux" and (self.options.with_wayland
                 or self.options.with_x11)) or self.options["pango"].with_freetype:
                self.cpp_info.components["gtk+-3.0"].requires.append("pango::pangoft2")
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

            self.cpp_info.requires.extend([
                "gdk-pixbuf::gdk-pixbuf", "glib::gobject-2.0", "glib::gmodule-2.0",
                "cairo::cairo", "cairo:::cairo-gobjec", "pango::pangocairo",
                "libpng::libpng", "libtiff::libtiff", "libjpeg::libjpeg",
                "libepoxy::libepoxy", "graphene::graphene-gobject-1.0",
                "fribidi::fribidi"
            ])
            if self.settings.os == "Linux":
                if self.options.with_x11:
                    self.cpp_info.requires.append("xorg::xorg")
                if self.options.with_wayland:
                    self.cpp_info.requires.append("xkbcommon::libxkbcommon")

            if (self.settings.os == "Linux" and (self.options.with_wayland
                 or self.options.with_x11)) or self.options["pango"].with_freetype:
                self.cpp_info.requires.append("pango::pangoft2")

    def package_id(self):
        self.info.requires["glib"].full_package_mode()
        self.info.requires["cairo"].full_package_mode()
        self.info.requires["pango"].full_package_mode()
        self.info.requires["gdk-pixbuf"].full_package_mode()
        if self._gtk3:
            self.info.requires["atk"].full_package_mode()
            if self.settings.os == "Linux" and self.options.with_x11:
                self.info.requires["at-spi2-atk"].full_package_mode()

        if self._gtk4:
            self.info.requires["graphene"].full_package_mode()
