import os
import textwrap

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class HighFiveConan(ConanFile):
    name = "highfive"
    description = "HighFive is a modern header-only C++11 friendly interface for libhdf5."
    license = "Boost Software License 1.0"
    topics = ("conan", "hdf5", "hdf", "data")
    homepage = "https://github.com/BlueBrain/HighFive"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_boost": [True, False],
    }
    default_options = {
        "with_boost": False,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        self.requires("hdf5/1.10.6")
        if self.options.with_boost:
            self.requires("boost/1.77.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["USE_BOOST"] = self.options.with_boost
        self._cmake.definitions["USE_EIGEN"] = "OFF"
        self._cmake.definitions["USE_XTENSOR"] = "OFF"
        self._cmake.definitions["USE_OPENCV"] = "OFF"
        self._cmake.definitions["HIGHFIVE_UNIT_TESTS"] = "OFF"
        self._cmake.definitions["HIGHFIVE_EXAMPLES"] = "OFF"
        self._cmake.definitions["HIGHFIVE_BUILD_DOCS"] = "OFF"
        self._cmake.definitions["HIGHFIVE_USE_INSTALL_DEPS"] = "OFF"
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package_id(self):
        self.info.header_only()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "HighFive"
        self.cpp_info.names["cmake_find_package_multi"] = "HighFive"
        self.cpp_info.requires = ["hdf5::hdf5_cpp"]
        if self.options.with_boost:
            self.cpp_info.requires.append("boost::headers")
