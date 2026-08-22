import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rename

required_conan_version = ">=2.0"


class NanobindConan(ConanFile):
    name = "nanobind"
    description = "Tiny and efficient C++/Python bindings"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/wjakob/nanobind"
    topics = ("python", "bindings", "nanobind", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def requirements(self):
        self.requires("tsl-robin-map/[>=1.3.0 <2]")

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["NB_TEST"] = False
        tc.cache_variables["NB_USE_SUBMODULE_DEPS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        # Don't generate any CMake files and include the upstream ones
        # Only CMake is officially supported by nanobind: 
        # https://nanobind.readthedocs.io/en/latest/building.html#building
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.builddirs.append(os.path.join("nanobind", "cmake"))
        self.cpp_info.includedirs = [os.path.join("nanobind", "include")]
