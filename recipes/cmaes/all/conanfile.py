from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import export_conandata_patches, get, rmdir, rm, copy
import os

class CmaesConan(ConanFile):
    name = "cmaes"

    generators = "CMakeDeps"

    # Optional metadata
    license = "LGPLv3"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/CMA-ES/libcmaes"
    description = "libcmaes is a multithreaded C++11 library with Python bindings for high performance blackbox stochastic optimization using the CMA-ES algorithm for Covariance Matrix Adaptation Evolution Strategy"
    topics = ("cmaes", "minimization")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "openmp": [True, False],
        "surrog": [True, False],
    }
    default_options = {
        "shared": False,
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
        if self.options.openmp:
            self.requires("llvm-openmp/17.0.6", transitive_headers=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self,src_folder="src")

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
        #apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib","pkgconfig"))
        rm(self, "*.cmake", os.path.join(self.package_folder, "lib", "cmake", "libcmaes"))
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.libs = ["cmaes"]
        self.cpp_info.set_property("cmake_target_name", "libcmaes::cmaes")
