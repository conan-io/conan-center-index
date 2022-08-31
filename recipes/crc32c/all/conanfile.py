from conan import ConanFile
from conan.tools.build import check_min_cppstd, valid_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=1.50.0"


class crc32cConan(ConanFile):
    name = "crc32c"
    description = "CRC32C implementation with support for CPU-specific acceleration instructions"
    topics = ("crc32c", "crc")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/crc32c"
    license = "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if not valid_min_cppstd(self, 11):
            tc.variables["CMAKE_CXX_STANDARD"] = 11
        tc.variables["CRC32C_BUILD_TESTS"] = False
        tc.variables["CRC32C_BUILD_BENCHMARKS"] = False
        tc.variables["CRC32C_INSTALL"] = True
        tc.variables["CRC32C_USE_GLOG"] = False
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Crc32c")
        self.cpp_info.set_property("cmake_target_name", "Crc32c::crc32c")

        # TODO: back to global scope once cmake_find_package* generators removed
        self.cpp_info.components["_crc32c"].libs = ["crc32c"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "Crc32c"
        self.cpp_info.names["cmake_find_package_multi"] = "Crc32c"
        self.cpp_info.components["_crc32c"].names["cmake_find_package"] = "crc32c"
        self.cpp_info.components["_crc32c"].names["cmake_find_package_multi"] = "crc32c"
        self.cpp_info.components["_crc32c"].set_property("cmake_target_name", "Crc32c::crc32c")
