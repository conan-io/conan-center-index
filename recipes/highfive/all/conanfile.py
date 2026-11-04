from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=2.1"

class HighFiveConan(ConanFile):
    name = "highfive"
    description = "User-friendly, header-only, C++14 wrapper for HDF5."
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/highfive-devs/highfive"
    topics = ("hdf5", "hdf", "data", "header-only")
    package_type = "header-library"
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
        "with_opencv": False,
    }

    def config_options(self):
        if Version(self.version) >= 3:
            del self.options.with_boost

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("hdf5/1.14.3")

        if self.options.get_safe("with_boost"):
            self.requires("boost/1.85.0")
        if self.options.with_xtensor:
            self.requires("xtensor/0.24.7")
        if self.options.with_opencv:
            self.requires("opencv/[>=4.8.1 <5]")
        if self.options.with_eigen:
            self.requires("eigen/[>=3.4.0 <4]")

    def package_id(self):
        # INFO: We only set different compiler definitions. The package content is the same.
        self.info.clear()

    def validate(self):
        if Version(self.version) < "3.0.0":
            check_min_cppstd(self, 11)
        else:
            check_min_cppstd(self, 14)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) < "3.0.0":
            tc.cache_variables["USE_BOOST"] = self.options.get_safe("with_boost")
            tc.cache_variables["USE_EIGEN"] = self.options.with_eigen
            tc.cache_variables["USE_XTENSOR"] = self.options.with_xtensor
            tc.cache_variables["USE_OPENCV"] = self.options.with_opencv
            tc.cache_variables["HIGHFIVE_USE_INSTALL_DEPS"] = False
            tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5"

        tc.cache_variables["HIGHFIVE_UNIT_TESTS"] = False
        tc.cache_variables["HIGHFIVE_EXAMPLES"] = False
        tc.cache_variables["HIGHFIVE_BUILD_DOCS"] = False

        tc.generate()
        deps = CMakeDeps(self)
        deps.set_property("eigen", "cmake_file_name", "Eigen3")
        deps.set_property("eigen", "cmake_additional_variables_prefixes", ["EIGEN3"])
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "HighFive")
        if Version(self.version) < "3.0.0":
            self.cpp_info.set_property("cmake_target_name", "HighFive")
        else:
            self.cpp_info.set_property("cmake_target_name", "HighFive::HighFive")

        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.requires = ["hdf5::hdf5"]
        if self.options.get_safe("with_boost"):
            self.cpp_info.requires.append("boost::headers")
            self.cpp_info.defines.append("H5_USE_BOOST")
        if self.options.with_eigen:
            self.cpp_info.requires.append("eigen::eigen")
            self.cpp_info.defines.append("H5_USE_EIGEN")
        if self.options.with_xtensor:
            self.cpp_info.requires.append("xtensor::xtensor")
            self.cpp_info.defines.append("H5_USE_XTENSOR")
        if self.options.with_opencv:
            self.cpp_info.requires.append("opencv::opencv")
            self.cpp_info.defines.append("H5_USE_OPENCV")
