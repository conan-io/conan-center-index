from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.build import check_min_cppstd
import os

required_conan_version = ">=2.0.0"


class LielabConan(ConanFile):
    name = "lielab"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/sandialabs/Lielab"
    description = "Lielab is a C++ library for numerical Lie-theory: Lie groups," \
                  " Lie algebras, homogeneous manifolds, and various functions and algorithms" \
                  " on these spaces."
    topics = ("Lie-theory", "Lie-group", "Lie-algebra", "numerical", "static-library")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    license = "MIT"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        self.requires("eigen/[>=5.0.0 <6]", transitive_headers=True)

    def validate(self):
        check_min_cppstd(self, 20)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.23 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LIELAB_INSTALL_LIBRARY"] = True
        tc.variables["LIELAB_BUILD_TESTS"] = False
        tc.variables["LIELAB_BUILD_PYTHON"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.configure()
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Lielab")
        self.cpp_info.set_property("cmake_target_name", "Lielab::Lielab")
        self.cpp_info.libs = ["Lielab"]
