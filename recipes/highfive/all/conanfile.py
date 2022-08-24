from from conan import ConanFile, tools
from conans import CMake
import os.path

required_conan_version = ">=1.33.0"


class HighFiveConan(ConanFile):
    name = "highfive"
    description = "HighFive is a modern header-only C++11 friendly interface for libhdf5."
    license = "Boost Software License 1.0"
    topics = ("hdf5", "hdf", "data")
    homepage = "https://github.com/BlueBrain/HighFive"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_boost": [True, False],
        "with_eigen": [True, False],
        "with_xtensor": [True, False],
        "with_opencv": [True, False],
    }
    default_options = {
        "with_boost": True,
        "with_eigen": True,
        "with_xtensor": True,
        "with_opencv": True,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        self.requires("hdf5/1.12.0")
        if self.options.with_boost:
            self.requires("boost/1.77.0")
        if self.options.with_eigen:
            self.requires("eigen/3.4.0")
        if self.options.with_xtensor:
            self.requires("xtensor/0.23.10")
        if self.options.with_opencv:
            self.requires("opencv/4.5.3")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def build(self):
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "CMake", "HighFiveTargetDeps.cmake"),
            "find_package(Eigen3 NO_MODULE)",
            "find_package(Eigen3 REQUIRED)",
        )
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "CMake", "HighFiveTargetDeps.cmake"),
            "EIGEN3_INCLUDE_DIRS",
            "Eigen3_INCLUDE_DIRS",
        )

        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["USE_BOOST"] = self.options.with_boost
        self._cmake.definitions["USE_EIGEN"] = self.options.with_eigen
        self._cmake.definitions["USE_XTENSOR"] = self.options.with_xtensor
        self._cmake.definitions["USE_OPENCV"] = self.options.with_opencv
        self._cmake.definitions["HIGHFIVE_UNIT_TESTS"] = False
        self._cmake.definitions["HIGHFIVE_EXAMPLES"] = False
        self._cmake.definitions["HIGHFIVE_BUILD_DOCS"] = False
        self._cmake.definitions["HIGHFIVE_USE_INSTALL_DEPS"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package_id(self):
        self.info.header_only()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "HighFive"
        self.cpp_info.names["cmake_find_package_multi"] = "HighFive"
        self.cpp_info.requires = ["hdf5::hdf5"]
        if self.options.with_boost:
            self.cpp_info.requires.append("boost::headers")
        if self.options.with_eigen:
            self.cpp_info.requires.append("eigen::eigen")
        if self.options.with_xtensor:
            self.cpp_info.requires.append("xtensor::xtensor")
        if self.options.with_opencv:
            self.cpp_info.requires.append("opencv::opencv")
