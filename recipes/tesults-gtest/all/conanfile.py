from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
import os

required_conan_version = ">=1.53.0"


class TesultsGtestConan(ConanFile):
    name = "tesults-gtest"
    description = "Google Test event listener for reporting test results to Tesults"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tesults/tesults-gtest"
    topics = ("tesults", "googletest", "testing", "test-results", "reporting")
    package_type = "header-library"
    settings = "os", "compiler", "build_type", "arch"
    no_copy_source = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("gtest/[>=1.11.0 <2]")
        self.requires("tesults-cpp/[>=1.0.2 <2]")

    def validate(self):
        check_min_cppstd(self, 17)

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_file_name", "tesults-gtest")
        self.cpp_info.set_property("cmake_target_name", "tesults_gtest::tesults_gtest")
