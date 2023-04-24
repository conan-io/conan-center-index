import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir

required_conan_version = ">=1.53.0"


class LibCuckooConan(ConanFile):
    name = "libcuckoo"
    description = "A high-performance, concurrent hash table"
    license = "Apache-2.0"
    homepage = "https://github.com/efficient/libcuckoo"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("concurrency", "hashmap", "header-only", "library", "cuckoo")
    settings = "arch", "build_type", "compiler", "os"

    @property
    def _minimum_cpp_standard(self):
        return 11

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_STRESS_TESTS"] = False
        tc.variables["BUILD_TESTS"] = False
        tc.variables["BUILD_UNIT_TESTS"] = False
        tc.variables["BUILD_UNIVERSAL_BENCHMARK"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        # Install with CMake
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))


    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libcuckoo")
        self.cpp_info.set_property("cmake_target_name", "libcuckoo::libcuckoo")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
