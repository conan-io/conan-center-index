from conans import ConanFile, Meson, RunEnvironment, tools
from conan.errors import ConanInvalidConfiguration
import os
import glob


class AravisConan(ConanFile):
    name = "aravis"
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/AravisProject/aravis"
    description = "A vision library for genicam based cameras."
    topics = ("usb", "camera")
    settings = "os", "compiler", "build_type", "arch"
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
        "gst_plugin": False,
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

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.packet_socket

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        self.options["glib"].shared = True

    def validate(self):
        if self._is_msvc and self.settings.get_safe("compiler.runtime", "").startswith("MT"):
            raise ConanInvalidConfiguration("Static MT/MTd runtime is not supported on Windows due to GLib issues")
        if not self.options["glib"].shared and self.options.shared:
            raise ConanInvalidConfiguration("Shared Aravis cannot link to static GLib")
        if self.settings.os == "Macos":
            raise ConanInvalidConfiguration("macOS builds are disabled until conan-io/conan#7324 gets merged to fix macOS SIP issue #8443")

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

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def _configure_meson(self):
        if self._meson:
            return self._meson
        defs = dict()
        defs["wrap_mode"] = "nofallback"
        defs["usb"] = "enabled" if self.options.usb else "disabled"
        defs["gst-plugin"] = "enabled" if self.options.gst_plugin else "disabled"
        defs["packet-socket"] = "enabled" if self.options.get_safe("packet_socket") else "disabled"
        defs["introspection"] = "enabled" if self.options.introspection else "disabled"
        defs["viewer"] = "disabled"
        defs["tests"] = "false"
        defs["documentation"] = "disabled"
        if self.settings.get_safe("compiler.runtime"):
            defs["b_vscrt"] = str(self.settings.compiler.runtime).lower()
        self._meson = Meson(self)
        self._meson.configure(defs=defs, source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._meson

    def build(self):
        self._patch_sources()
        with tools.environment_append(RunEnvironment(self).vars):
            meson = self._configure_meson()
            meson.build()

    def _fix_library_names(self, path):
        # https://github.com/mesonbuild/meson/issues/1412
        if not self.options.shared and self._is_msvc:
            with tools.chdir(path):
                for filename_old in glob.glob("*.a"):
                    filename_new = filename_old[3:-2] + ".lib"
                    self.output.info("rename %s into %s" % (filename_old, filename_new))
                    tools.rename(filename_old, filename_new)

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses", keep_path=False)
        with tools.environment_append(RunEnvironment(self).vars):
            meson = self._configure_meson()
            meson.install()

        self._fix_library_names(os.path.join(self.package_folder, "lib"))
        if self.options.gst_plugin:
            self._fix_library_names(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(self.package_folder, "*.pdb")
        if not self.options.tools:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "arv-*")

    def package_id(self):
        self.info.requires["glib"].full_package_mode()
        if self.options.gst_plugin:
            self.info.requires["gstreamer"].full_package_mode()
            self.info.requires["gst-plugins-base"].full_package_mode()

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
