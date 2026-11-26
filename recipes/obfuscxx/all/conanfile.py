from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os


required_conan_version = ">=2.0"


class ObfuscxxConan(ConanFile):
    name = "obfuscxx"
    description = "Header-only compile-time variable obfuscation library for C++20"
    license = "Apache-2.0"
    homepage = "https://github.com/nevergiveupcpp/obfuscxx"
    url = "https://github.com/conan-io/conan-center-index"
    topics = (
        "anti-analysis",
        "compile-time",
        "constant-obfuscation",
        "constexpr",
        "cpp",
        "cpp20",
        "header-only",
        "obfuscation",
        "obfuscator",
        "simd",
        "string-encryption",
        "string-obfuscation",
        "xtea",
    )
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 20)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        CMakeToolchain(self).generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        CMake(self).install()
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "obfuscxx")
        self.cpp_info.set_property("cmake_target_name", "obfuscxx::obfuscxx")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
