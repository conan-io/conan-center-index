from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy, rmdir
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=2.0"

class KDAlgorithmsConan(ConanFile):
    name = "kdalgorithms"
    license = "MIT"
    description = "C++ Algorithm wrappers"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/KDAB/KDAlgorithms"
    topics = ("c++14", "algorithmns", "kdab", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def validate(self):
        check_min_cppstd(self, "14")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_TESTING"] = False
        tc.generate()

    def package(self):
        copy(self, "LICENSES/*", dst=os.path.join(self.package_folder,"licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.configure()
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))


    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_file_name", "KDAlgorithms")
        self.cpp_info.set_property("cmake_target_name", "KDAB::kdalgorithms")
