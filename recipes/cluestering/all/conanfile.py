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
    description = "CLUEstering is a density-based weighted clustering library based on a highly parallel and scalable algorithm, CLUE, which was developed at CERN. The library is designed to be performance portable, supporting both CPU and GPU architectures, and is implemented in C++20 using the Alpaka framework for heterogeneous computing. CLUEstering is suitable for high-performance computing environments and can be used in various applications requiring efficient clustering of large datasets."
    topics = ("clustering", "density-based/weighted", "gpu", "hpc", "performance-portability", "alpaka")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    license = "MPL-2.0"

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    def layout(self):
        cmake_layout(self)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

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
