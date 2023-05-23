from conan import ConanFile
from conan.tools.build import check_min_cppstd, valid_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=1.53.0"


class crc32cConan(ConanFile):
    name = "crc32c"
    description = "CRC32C implementation with support for CPU-specific acceleration instructions"
    topics = ("crc32c", "crc")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/crc32c"
    license = "BSD-3-Clause"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return "11"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if not valid_min_cppstd(self, self._min_cppstd):
            tc.variables["CMAKE_CXX_STANDARD"] = self._min_cppstd
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
