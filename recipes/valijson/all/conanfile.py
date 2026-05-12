from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy, rmdir
from conan.tools.cmake import cmake_layout, CMakeToolchain, CMake
import os

required_conan_version = ">=2.1"


class ValijsonConan(ConanFile):
    name = "valijson"
    description = "Valijson is a header-only JSON Schema Validation library for C++11."
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tristanpenman/valijson"
    topics = ("json", "validator", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_target_name", "ValiJSON::valijson")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.components["libvalijson"].set_property("cmake_target_name", "ValiJSON::valijson")
        self.cpp_info.components["libvalijson"].bindirs = []
        self.cpp_info.components["libvalijson"].libdirs = []
