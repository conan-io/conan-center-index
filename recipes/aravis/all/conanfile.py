from conans import ConanFile, Meson, tools
from conans.errors import ConanInvalidConfiguration
import os
import glob
import shutil


class AravisConan(ConanFile):
    name = "aravis"
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/AravisProject/aravis"
    description = "A vision library for genicam based cameras."
    topics = ("usb", "camera")
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = ["patches/**"]
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "usb": [True, False],
        "packet_socket": [True, False],
        "gst_plugin": [True, False],
        "tools": [True, False],
        "introspection": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "usb": True,
        "packet_socket": True,
        "gst_plugin": True,
        "tools": True,
        "introspection": False
    }
    generators = "pkg_config"

    _meson = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _aravis_api_version(self):
        return ".".join(self.version.split(".")[0:2])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.packet_socket

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if not self.options["glib"].shared and self.options.shared:
            raise ConanInvalidConfiguration("shared Aravis cannot link to static GLib")

    def build_requirements(self):
        self.build_requires("meson/0.60.2")
        self.build_requires("pkgconf/1.7.4")
        if self.options.introspection:
            self.build_requires("gobject-introspection/1.70.0")

    def requirements(self):
        self.requires("glib/2.70.1")
        self.requires("libxml2/2.9.12")
        self.requires("zlib/1.2.11")
        if self.options.usb:
            self.requires("libusb/1.0.24")
        if self.options.gst_plugin:
            self.requires("gstreamer/1.19.2")
            self.requires("gst-plugins-base/1.19.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def _configure_meson(self):
        if self._meson:
            return self._meson
        defs = dict()
        defs["usb"] = "enabled" if self.options.usb else "disabled"
        defs["gst-plugin"] = "enabled" if self.options.gst_plugin else "disabled"
        if self.options.get_safe("packet_socket"):
            defs["packet-socket"] = "enabled" if self.options.packet_socket else "disabled"
        defs["introspection"] = "enabled" if self.options.introspection else "disabled"
        defs["viewer"] = "disabled"
        defs["tests"] = "false"
        defs["documentation"] = "disabled"
        self._meson = Meson(self)
        self._meson.configure(defs=defs, source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._meson

    def build(self):
        self._patch_sources()
        meson = self._configure_meson()
        meson.build()

    def _fix_library_names(self, path):
        # https://github.com/mesonbuild/meson/issues/1412
        if not self.options.shared and self.settings.compiler == "Visual Studio":
            with tools.chdir(path):
                for filename_old in glob.glob("*.a"):
                    filename_new = filename_old[3:-2] + ".lib"
                    self.output.info("rename %s into %s" % (filename_old, filename_new))
                    shutil.move(filename_old, filename_new)

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses", keep_path=False)
        meson = self._configure_meson()
        meson.install()

        self._fix_library_names(os.path.join(self.package_folder, "lib"))
        self._fix_library_names(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(self.package_folder, "*.pdb")
        if not self.options.tools:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "arv-*")

    def package_id(self):
        self.info.requires["glib"].full_package_mode()

    def package_info(self):
        aravis_name = "aravis-{}".format(self._aravis_api_version)
        self.cpp_info.names["pkg_config"] = aravis_name
        self.cpp_info.includedirs = [os.path.join("include", aravis_name)]
        self.cpp_info.libs = [aravis_name]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "pthread", "m", "resolv"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "iphlpapi"])

        if self.options.tools:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
        if self.options.gst_plugin and self.options.shared:
            gst_plugin_path = os.path.join(self.package_folder, "lib", "gstreamer-1.0")
            self.output.info("Appending GST_PLUGIN_PATH env var: {}".format(gst_plugin_path))
            self.env_info.GST_PLUGIN_PATH.append(gst_plugin_path)
