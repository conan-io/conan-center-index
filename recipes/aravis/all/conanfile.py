from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, export_conandata_patches, apply_conandata_patches, rename, chdir, rm, rmdir
from conan.tools.microsoft import is_msvc
from conans import Meson, RunEnvironment, tools
import os
import glob

required_conan_version = ">=1.52.0"

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
        if is_msvc(self) and self.settings.get_safe("compiler.runtime", "").startswith("MT"):
            raise ConanInvalidConfiguration("Static MT/MTd runtime is not supported on Windows due to GLib issues")
        if not self.options["glib"].shared and self.options.shared:
            raise ConanInvalidConfiguration("Shared Aravis cannot link to static GLib")
        if self.settings.os == "Macos":
            raise ConanInvalidConfiguration("macOS builds are disabled until conan-io/conan#7324 gets merged to fix macOS SIP issue #8443")

    def build_requirements(self):
        self.build_requires("meson/0.63.3")
        self.build_requires("pkgconf/1.9.3")
        if self.options.introspection:
            self.build_requires("gobject-introspection/1.72.0")

    def requirements(self):
        self.requires("glib/2.74.0")
        self.requires("libxml2/2.9.14")
        self.requires("zlib/1.2.12")
        if self.options.usb:
            self.requires("libusb/1.0.26")
        if self.options.gst_plugin:
            self.requires("gstreamer/1.19.2")
            self.requires("gst-plugins-base/1.19.2")

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

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
        apply_conandata_patches(self)
        with tools.environment_append(RunEnvironment(self).vars):
            meson = self._configure_meson()
            meson.build()

    def _fix_library_names(self, path):
        # https://github.com/mesonbuild/meson/issues/1412
        if not self.options.shared and is_msvc(self):
            with chdir(self, path):
                for filename_old in glob.glob("*.a"):
                    filename_new = filename_old[3:-2] + ".lib"
                    self.output.info(f"rename {filename_old} into {filename_new}")
                    rename(self, filename_old, filename_new)

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses", keep_path=False)
        with tools.environment_append(RunEnvironment(self).vars):
            meson = self._configure_meson()
            meson.install()

        self._fix_library_names(os.path.join(self.package_folder, "lib"))
        if self.options.gst_plugin:
            self._fix_library_names(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", self.package_folder, recursive=True)
        if not self.options.tools:
            rm(self, "arv-*", os.path.join(self.package_folder, "bin"))

    def package_id(self):
        self.info.requires["glib"].full_package_mode()
        if self.options.gst_plugin:
            self.info.requires["gstreamer"].full_package_mode()
            self.info.requires["gst-plugins-base"].full_package_mode()

    def package_info(self):
        aravis_name = f"aravis-{self._aravis_api_version}"
        self.cpp_info.names["pkg_config"] = aravis_name
        self.cpp_info.includedirs = [os.path.join("include", aravis_name)]
        self.cpp_info.libs = [aravis_name]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "pthread", "m", "resolv"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "iphlpapi"])

        if self.options.tools:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info(f"Appending PATH environment variable: {bin_path}")
            self.env_info.PATH.append(bin_path)
        if self.options.gst_plugin and self.options.shared:
            gst_plugin_path = os.path.join(self.package_folder, "lib", "gstreamer-1.0")
            self.output.info(f"Appending GST_PLUGIN_PATH env var: {gst_plugin_path}")
            self.env_info.GST_PLUGIN_PATH.append(gst_plugin_path)
