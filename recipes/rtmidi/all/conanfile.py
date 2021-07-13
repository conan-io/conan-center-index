import os
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.33.0"


class RtMidiConan(ConanFile):
    name = "rtmidi"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.music.mcgill.ca/~gary/rtmidi/"
    description = "Realtime MIDI input/output"
    topics = ("midi")
    license = "Copyright (c) 2003-2019 Gary P. Scavone"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "pkg_config"
    exports_sources = "patches/*"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        }
    default_options = {
        "shared": False,
        "fPIC": True,
        }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    _cmake = None

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.settings.os == "Linux":
            self.requires("libalsa/1.2.4")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
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
        self.cpp_info.names["pkg_config"] = "rtmidi"
        self.cpp_info.libs = ["rtmidi"]
        if self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(
                ["CoreFoundation", "CoreAudio", "CoreMidi"]
            )
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("winmm")
        elif self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs.append("pthread")
