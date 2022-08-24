from conan import ConanFile, tools
from conan.tools.cmake import CMake
from conan.errors import ConanInvalidConfiguration
import os


class LibyuvConan(ConanFile):
    name = "libyuv"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://chromium.googlesource.com/libyuv/libyuv/"
    description = "libyuv is an open source project that includes YUV scaling and conversion functionality."
    topics = ["YUV", "libyuv", "google", "chromium"]
    license = "BSD-3-Clause"
    settings = "os", "compiler", "arch", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "with_jpeg": [False, "libjpeg", "libjpeg-turbo"]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "with_jpeg": "libjpeg"}
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if str(self.options.with_jpeg) == "libjpeg-turbo":
            raise ConanInvalidConfiguration(
                "libjpeg-turbo is an invalid option right now, as it is not supported by the cmake script.")

    def requirements(self):
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9d")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.0.5")

    def source(self):
        tools.get(**self.conan_data["sources"]
                  [self.version], destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        if not self.options.with_jpeg:
            self._cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_JPEG"] = True

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

    def package_info(self):
        self.cpp_info.libs = ["yuv"]
