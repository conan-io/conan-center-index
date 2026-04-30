from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rmdir
import os

required_conan_version = ">=2.1"


class CLUEsteringConan(ConanFile):
    name = "cluestering"
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

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "CLUEstering")
        self.cpp_info.set_property("cmake_target_name", "CLUEstering::CLUEstering")
        self.cpp_info.includedirs = ["include"]
