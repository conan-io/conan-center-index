from conan import ConanFile
from conan.tools.files import get, copy, apply_conandata_patches
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.50.0"


class CLUEsteringConan(ConanFile):
    name = "cluestering"
    version = "2.9.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cms-patatrack/CLUEstering"
    description = (
        "CLUEstering is a density-based weighted clustering library "
        "designed for high-performance computing applications."
    )
    topics = ("clustering", "density-based/weighted", "gpu", "hpc", "performance-portability", "alpaka")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    license = "MPL-2.0"

    def requirements(self):
        self.requires("alpaka/2.1.1", transitive_headers=True)
        self.requires("boost/[>=1.74.0 <2]", transitive_headers=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 20)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def package_id(self):
        self.info.clear()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE", dst=self.package_folder, src=self.source_folder)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "cluestering")
        self.cpp_info.set_property("cmake_target_name", "CLUEstering::CLUEstering")
        self.cpp_info.includedirs = ["include"]
