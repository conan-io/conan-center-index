from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, cmake_layout, CMakeToolchain
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=2.1"


class FcarougeKalmanConan(ConanFile):
    name = "fcarouge-kalman"
    description = "Kalman filters C++ library."
    license = "Unlicense"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/FrancoisCarouge/Kalman"
    topics = ("kalman", "control", "filter", "estimation")
    package_type = "header-library"
    settings = "compiler", "os", "build_type", "arch"

    implements = ["auto_header_only"]

    def validate(self):
        check_min_cppstd(self, 23)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.variables["BUILD_TESTING"] = False
        toolchain.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(
            self,
            "LICENSE.txt",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "fcarouge-kalman")
        self.cpp_info.set_property("cmake_target_name", "fcarouge-kalman::kalman")
        self.cpp_info.set_property("pkg_config_name", "fcarouge-kalman")
        self.cpp_info.libs = ["fcarouge-kalman"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.bindirs = []
