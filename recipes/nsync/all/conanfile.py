import os
from conans import ConanFile, CMake, tools


class NsyncConan(ConanFile):
    name = "nsync"
    description = "Library that exports various synchronization primitive"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("c", "thread", "multithreading", "google")
    settings = "os", "compiler", "build_type", "arch"

    options = {"with_tests": [True, False]}
    default_options = {"with_tests": False}

    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["NSYNC_ENABLE_TESTS"] = self.options.with_tests
        self._cmake.configure(
            build_folder=self._build_subfolder,
            source_folder=self._source_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.nsync_cpp.libs = ["nsync_cpp"]
        self.cpp_info.nsync.libs = ["nsync"]
