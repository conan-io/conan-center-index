import os
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.43.0"


class RtMidiConan(ConanFile):
    name = "rtmidi"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.music.mcgill.ca/~gary/rtmidi/"
    description = "Realtime MIDI input/output"
    topics = ("midi")
    license = "MIT+send-patches-upstream"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "pkg_config"
    exports_sources = "CMakeLists.txt", "patches/*"
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

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self._with_alsa:
            self.requires("libalsa/1.2.4")

    def build_requirements(self):
        if self._with_alsa:
            self.build_requires("pkgconf/1.7.4")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["RTMIDI_BUILD_TESTING"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        if tools.Version(self.version) >= "5.0.0":
            self.cpp_info.components["librtmidi"].includedirs = [os.path.join("include", "rtmidi")]

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
