import re, os, functools

from conan import ConanFile, tools
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import load, export_conandata_patches, get
from conan.tools.env import Environment

from conan.tools.scm import Git


class CmaesConan(ConanFile):
    name = "libcmaes"

    generators = "CMakeDeps"

    # Optional metadata
    license = "MIT"
    author = "Philipp Basler"
    url = "https://github.com/CMA-ES/libcmaes"
    description = "libcmaes is a multithreaded C++11 library with Python bindings for high performance blackbox stochastic optimization using the CMA-ES algorithm for Covariance Matrix Adaptation Evolution Strategy"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "openmp": [True, False],
        "surrog": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "openmp": True,
        "surrog": True,
    }

    short_paths = True

    def export_sources(self):
        export_conandata_patches(self)
    
    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build_requirements(self):
        pass

    def requirements(self):
        self.requires("eigen/3.4.0", transitive_headers=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LIBCMAES_BUILD_EXAMPLES"] = False
        tc.variables["LIBCMAES_BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["LIBCMAES_USE_OPENMP"] = self.options.openmp
        tc.variables["LIBCMAES_ENABLE_SURROG"] = self.options.surrog
        tc.variables["LIBCMAES_BUILD_PYTHON"] = False
        tc.variables["LIBCMAES_BUILD_TESTS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["cmaes"]
        self.cpp_info.set_property("cmake_target_name", "libcmaes::cmaes")
