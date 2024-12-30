import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir

required_conan_version = ">=1.53.0"


class LapackConan(ConanFile):
    name = "lapack"
    description = "LAPACK is a library of Fortran subroutines for solving the most commonly occurring problems in numerical linear algebra"
    license = "BSD-3-Clause-Open-MPI"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Reference-LAPACK/lapack"
    topics = ("linear-algebra", "matrix-factorization", "linear-equations", "svd", "singular-values", "eigenvectors", "eigenvalues")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_deprecated": [True, False],
        "single": [True, False],
        "double": [True, False],
        "complex": [True, False],
        "complex16": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_deprecated": False,
        "single": True,
        "double": True,
        "complex": True,
        "complex16": True,
    }
    options_description = {
        "build_deprecated": "Build deprecated routines",
        "single": "Build single precision real",
        "double": "Build double precision real",
        "complex": "Build single precision complex",
        "complex16": "Build double precision complex",
    }

    def config_options(self):
        del self.options.fPIC

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openblas/0.3.28")
        self.requires("gfortran/13.2.0")

    def validate(self):
        if self.settings.os == "Windows":
            # Can probably use GFortran from MinGW or MSYS2 for this.
            # Another alternative might be to use the Intel Fortran compiler.
            raise ConanInvalidConfiguration("No Fortran compiler currently available for Windows")

    def build_requirements(self):
        self.tool_requires("gfortran/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["BUILD_DEPRECATED"] = self.options.build_deprecated
        tc.variables["BUILD_SINGLE"] = self.options.single
        tc.variables["BUILD_DOUBLE"] = self.options.double
        tc.variables["BUILD_COMPLEX"] = self.options.complex
        tc.variables["BUILD_COMPLEX16"] = self.options.complex16
        tc.variables["USE_OPTIMIZED_BLAS"] = True
        tc.variables["USE_OPTIMIZED_LAPACK"] = False
        tc.variables["CBLAS"] = False
        tc.variables["LAPACKE"] = True
        # VerifyFortranC module in CMake fails to build a test executable otherwise.
        tc.variables["CMAKE_Fortran_FLAGS"] = "-fPIC"
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = True
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

        venv = VirtualBuildEnv(self)
        venv.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "module")
        self.cpp_info.set_property("cmake_file_name", "LAPACK")
        self.cpp_info.set_property("cmake_target_name", "LAPACK::LAPACK")

        self.cpp_info.components["lapack"].libs = ["lapack"]
        self.cpp_info.components["lapack"].set_property("cmake_target_name", "lapack")
        self.cpp_info.components["lapack"].set_property("pkg_config_name", "lapack")
        self.cpp_info.components["lapack"].requires = ["openblas::openblas", "gfortran::libgfortran"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["lapack"].system_libs.append("m")

        self.cpp_info.components["lapacke"].libs = ["lapacke"]
        self.cpp_info.components["lapacke"].set_property("cmake_target_name", "lapacke")
        self.cpp_info.components["lapacke"].set_property("pkg_config_name", "lapacke")
        self.cpp_info.components["lapacke"].requires = ["lapack"]
