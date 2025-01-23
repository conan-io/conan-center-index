import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rename

required_conan_version = ">=2.0"


class PackageConan(ConanFile):
    name = "nanobind"
    description = "Tiny and efficient C++/Python bindings"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/wjakob/nanobind"
    topics = ("python", "bindings", "pybind11", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def requirements(self):
        self.requires("tsl-robin-map/1.3.0")

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

    @property
    def _cmake_rel_dir(self):
        return os.path.join("lib", "cmake")

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rename(self,
               os.path.join(self.package_folder, "nanobind"),
               os.path.join(self.package_folder, "lib"))
        rename(self,
               os.path.join(self.package_folder, self._cmake_rel_dir, "nanobind-config.cmake"),
               os.path.join(self.package_folder, self._cmake_rel_dir, "nanobind.cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "nanobind")
        self.cpp_info.includedirs = [os.path.join("lib", "include")]
        self.cpp_info.builddirs = [self._cmake_rel_dir]
        self.cpp_info.set_property("cmake_build_modules", [os.path.join(self._cmake_rel_dir, "nanobind.cmake")])
