from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, rm, rmdir, replace_in_file
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
import os


required_conan_version = ">=2.4"


class Pipewire(ConanFile):
    name = "pipewire"
    description = "PipeWire is a server and user space API to deal with multimedia pipelines."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.freedesktop.org/pipewire/pipewire"
    topics = ("multimedia", "pipelines", "compatibility")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }
    languages = "C"
    implements = ["auto_shared_fpic"]

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("glib/[>=2.82 <3]")

    def validate(self):
        if self.settings.os not in ("Linux", "FreeBSD"):
            raise ConanInvalidConfiguration("Not supported on this platform.")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        replace_in_file(self, os.path.join(self.source_folder, "spa", "meson.build"), "subdir('tests')", "")
        replace_in_file(self, os.path.join(self.source_folder, "spa", "meson.build"), "subdir('examples')", "")

    def generate(self):
        tc = MesonToolchain(self)

        tc.project_options["alsa"] = "disabled"
        tc.project_options["audioconvert"] = "enabled"
        tc.project_options["audiomixer"] = "disabled"
        tc.project_options["audiotestsrc"] = "disabled"
        tc.project_options["avahi"] = "disabled"
        tc.project_options["bluez5-backend-hfp-native"] = "disabled"
        tc.project_options["bluez5-backend-hsp-native"] = "disabled"
        tc.project_options["bluez5-backend-hsphfpd"] = "disabled"
        tc.project_options["bluez5-backend-ofono"] = "disabled"
        tc.project_options["bluez5-codec-aac"] = "disabled"
        tc.project_options["bluez5-codec-aptx"] = "disabled"
        tc.project_options["bluez5-codec-lc3plus"] = "disabled"
        tc.project_options["bluez5-codec-ldac"] = "disabled"
        tc.project_options["bluez5"] = "disabled"
        tc.project_options["control"] = "disabled"
        tc.project_options["dbus"] = "disabled"
        tc.project_options["docs"] = "disabled"
        tc.project_options["echo-cancel-webrtc"] = "disabled"
        tc.project_options["evl"] = "disabled"
        tc.project_options["examples"] = "disabled"
        tc.project_options["ffmpeg"] = "disabled"
        tc.project_options["gstreamer-device-provider"] = "disabled"
        tc.project_options["gstreamer"] = "disabled"
        tc.project_options["installed_tests"] = "disabled"
        tc.project_options["jack-devel"] = "false"
        tc.project_options["jack"] = "disabled"
        tc.project_options["legacy-rtkit"] = "false"
        tc.project_options["libcamera"] = "disabled"
        tc.project_options["libcanberra"] = "disabled"
        tc.project_options["libpulse"] = "disabled"
        tc.project_options["libusb"] = "disabled"
        tc.project_options["lv2"] = "disabled"
        tc.project_options["man"] = "disabled"
        tc.project_options["opus"] = "disabled"
        tc.project_options["pipewire-alsa"] = "disabled"
        tc.project_options["pipewire-jack"] = "disabled"
        tc.project_options["pipewire-v4l2"] = "disabled"
        tc.project_options["pw-cat"] = "disabled"
        tc.project_options["raop"] = "disabled"
        tc.project_options["roc"] = "disabled"
        tc.project_options["sdl2"] = "disabled"
        tc.project_options["selinux"] = "disabled"
        tc.project_options["sndfile"] = "disabled"
        tc.project_options["spa-plugins"] = "enabled"
        tc.project_options["support"] = "enabled"
        tc.project_options["systemd-system-service"] = "disabled"
        tc.project_options["systemd-system-unit-dir"] = "disabled"
        tc.project_options["systemd-user-service"] = "disabled"
        tc.project_options["systemd-user-unit-dir"] = "disabled"
        tc.project_options["test"] = "disabled"
        tc.project_options["tests"] = "disabled"
        tc.project_options["udev"] = "disabled"
        tc.project_options["udevrulesdir"] = "disabled"
        tc.project_options["v4l2"] = "disabled"
        tc.project_options["videoconvert"] = "disabled"
        tc.project_options["videotestsrc"] = "disabled"
        tc.project_options["volume"] = "disabled"
        tc.project_options["vulkan"] = "disabled"
        tc.project_options["x11-xfixes"] = "disabled"
        tc.project_options["x11"] = "disabled"
        tc.project_options["session-managers"] = "[]"
        tc.project_options["c_args"] = "-Wno-strict-prototypes"
        tc.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.components["pipewire"].libs = ["pipewire-0.3"]
        self.cpp_info.components["pipewire"].includedirs = [os.path.join("include", "pipewire-0.3")]
        self.cpp_info.components["pipewire"].requires = ["glib::glib", "spa"]
        self.cpp_info.components["pipewire"].set_property("pkg_config_name", "libpipewire-0.3")
        self.cpp_info.components["pipewire"].set_property("pkg_config_custom_content", {"moduledir": "${libdir}/pipewire-0.3"})

        self.cpp_info.components["spa"].libs = ["spa"]
        self.cpp_info.components["spa"].libdirs = [os.path.join("lib", "spa-0.2")]
        self.cpp_info.components["spa"].includedirs = [os.path.join("include", "spa-0.2")]
        self.cpp_info.set_property("pkg_config_name", "libspa-0.2.pc")
        self.cpp_info.set_property("pkg_config_custom_content", {"plugindir": "${libdir}/spa-0.2"})

        self.cpp_info.components["pipewire"].system_libs.extend(["m", "pthread", "dl"])
        self.cpp_info.components["spa"].system_libs.extend(["m", "pthread", "dl"])
