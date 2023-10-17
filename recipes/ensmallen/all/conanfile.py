from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, replace_in_file, rmdir, copy

import os

required_conan_version = ">=2.0.12"

class ensmallenRecipe(ConanFile):
    name = "ensmallen"
    description = "ensmallen is a high quality C++ library for non-linear numerical optimization."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mlpack/ensmallen"
    topics = ("optimization", "numerical", "header-only")

    package_type = "header-library"
    settings = "os", "compiler", "build_type", "arch"

    def package_id(self):
        self.info.clear()

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("armadillo/12.2.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.set_property("armadillo", "cmake_file_name", "Armadillo")
        deps.set_property("armadillo", "cmake_target_name", "Armadillo::Armadillo")
        deps.set_property("armadillo", "cmake_config_version_compat", "AnyNewerVersion")
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["USE_OPENMP"] = False
        tc.generate()


    def build(self):
        cmake = CMake(self)
        cmake.configure()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        copy(self, "LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        rmdir(self, os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
