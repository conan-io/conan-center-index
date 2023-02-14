from conan import ConanFile
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.scm import Version
from conan.tools.env import VirtualBuildEnv
import os

required_conan_version = ">=1.53.0"


class RtMidiConan(ConanFile):
    name = "rtmidi"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.music.mcgill.ca/~gary/rtmidi/"
    description = "Realtime MIDI input/output"
    topics = ("midi")
    license = "MIT+send-patches-upstream"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        }
    default_options = {
        "shared": False,
        "fPIC": True,
        }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _with_alsa(self):
        return self.settings.os == "Linux"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self._with_alsa:
            self.requires("libalsa/1.2.4")

    def build_requirements(self):
        if self._with_alsa and not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/1.9.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["RTMIDI_BUILD_TESTING"] = False
        tc.generate()
        if self._with_alsa:
            tc = CMakeDeps(self)
            tc.generate()
            tc = VirtualBuildEnv(self)
            tc.generate(scope="build")


    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        if Version(self.version) < "5.0.0":
            os.makedirs(os.path.join(self.package_folder, "include", "rtmidi"))
            os.rename(
                os.path.join(self.package_folder, "include", "RtMidi.h"),
                os.path.join(self.package_folder, "include", "rtmidi", "RtMidi.h"),
            )

    def package_info(self):
        self.cpp_info.components["librtmidi"].includedirs = [os.path.join("include", "rtmidi")]

        self.cpp_info.set_property("cmake_module_file_name", "RtMidi")
        self.cpp_info.set_property("cmake_module_target_name", "RtMidi::rtmidi")
        self.cpp_info.set_property("cmake_file_name", "RtMidi")
        self.cpp_info.set_property("cmake_target_name", "RtMidi::rtmidi")
        self.cpp_info.components["librtmidi"].set_property("cmake_target_name", "RtMidi::rtmidi")
        self.cpp_info.set_property("pkg_config_name", "rtmidi")
        self.cpp_info.components["librtmidi"].set_property("pkg_config_name", "rtmidi")
        self.cpp_info.names["cmake_find_package"] = "RtMidi"
        self.cpp_info.names["cmake_find_package_multi"] = "RtMidi"
        self.cpp_info.components["librtmidi"].names["cmake_find_package"] = "rtmidi"
        self.cpp_info.components["librtmidi"].names["cmake_find_package_multi"] = "rtmidi"
        self.cpp_info.components["librtmidi"].libs = ["rtmidi"]
        if self._with_alsa:
            self.cpp_info.components["librtmidi"].requires.append("libalsa::libalsa")
        if self.settings.os == "Macos":
            self.cpp_info.components["librtmidi"].frameworks.extend(
                ["CoreFoundation", "CoreAudio", "CoreMidi"]
            )
        if self.settings.os == "Windows":
            self.cpp_info.components["librtmidi"].system_libs.append("winmm")
        elif self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.components["librtmidi"].system_libs.append("pthread")
