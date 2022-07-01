from conans import ConanFile, CMake, tools
import os
import textwrap

required_conan_version = ">=1.43.0"


class MiniaudioConan(ConanFile):
    name = "miniaudio"
    description = "A single file audio playback and capture library."
    topics = ("miniaudio", "header-only", "sound")
    homepage = "https://github.com/mackron/miniaudio"
    url = "https://github.com/conan-io/conan-center-index"
    license = ["Unlicense", "MIT-0"]
    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "header_only": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "header_only": True,
    }

    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        self.license = "miniaudio-{}".format(self.version)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["MINIAUDIO_VERSION_STRING"] = self.version
        self._cmake.configure()
        return self._cmake

    def build(self):
        if self.options.header_only:
            return

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses",
                  src=self._source_subfolder)
        self.copy(
            pattern="**",
            dst="include/extras",
            src=os.path.join(self._source_subfolder, "extras"),
        )

        if self.options.header_only:
            self.copy(pattern="miniaudio.h", dst="include",
                      src=self._source_subfolder)
            self.copy(
                pattern="miniaudio.*",
                dst="include/extras/miniaudio_split",
                src=os.path.join(self._source_subfolder,
                                 "extras/miniaudio_split"),
            )
        else:
            cmake = self._configure_cmake()
            cmake.install()

    def package_info(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("dl")
        if self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(
                ["CoreFoundation", "CoreAudio", "AudioUnit"]
            )
            self.cpp_info.defines.append("MA_NO_RUNTIME_LINKING=1")

        if not self.options.header_only:
            self.cpp_info.libs = ["miniaudio"]
            if self.options.shared:
                self.cpp_info.defines.append("MA_DLL")

    def package_id(self):
        if self.options.header_only:
            self.info.header_only()
