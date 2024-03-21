from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=1.52.0"

class LielabConan(ConanFile):
    name = "lielab"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/sandialabs/Lielab"
    description = "Lielab is a C++ library for numerical Lie-theory: Lie groups," \
                  " Lie algebras, homogeneous manifolds, and various functions and algorithms" \
                  " on these spaces."
    topics = ("Lie-theory", "Lie-group", "Lie-algebra", "numerical", "header-only")
    package_type = "header-library"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    
    no_copy_source = True

    def requirements(self):
        self.requires("eigen/3.4.0")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.23 <4]")
    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LIELAB_INSTALL_LIBRARY"] = True
        tc.variables["LIELAB_BUILD_TESTS"] = False
        tc.variables["LIELAB_BUILD_PYTHON"] = False
        tc.generate()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.configure()
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
    
    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "Lielab")
        self.cpp_info.set_property("cmake_target_name", "Lielab::Lielab")

        self.cpp_info.names["cmake_find_package"] = "Lielab"
        self.cpp_info.names["cmake_find_package_multi"] = "Lielab"
    
    def package_id(self):
        self.info.clear()

