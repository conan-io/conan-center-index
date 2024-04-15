import os
import re

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import get, rm, rmdir, load, save

required_conan_version = ">=1.53.0"


class SuiteSparseConfigConan(ConanFile):
    name = "suitesparse-config"
    description = "Configuration for SuiteSparse libraries"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://people.engr.tamu.edu/davis/suitesparse.html"
    topics = ("mathematics", "sparse-matrix", "linear-algebra")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openblas/0.3.26", transitive_headers=True, transitive_libs=True)
        self.requires("llvm-openmp/17.0.6", transitive_headers=True, transitive_libs=True)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.22 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        venv = VirtualBuildEnv(self)
        venv.generate()

        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["BUILD_STATIC_LIBS"] = not self.options.shared
        tc.variables["SUITESPARSE_USE_OPENMP"] = True
        tc.variables["SUITESPARSE_USE_CUDA"] = False
        tc.variables["BLA_VENDOR"] = "OpenBLAS"
        tc.variables["SUITESPARSE_DEMOS"] = False
        tc.variables["SUITESPARSE_USE_STRICT"] = True  # don't allow implicit dependencies
        tc.variables["SUITESPARSE_USE_FORTRAN"] = False  # Fortran sources are translated to C instead
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "SuiteSparse_config"))
        cmake.build()

    def _copy_license(self):
        # Extract the license applicable to SuiteSparse_config from all licenses in SuiteSparse
        full_license_info = load(self, os.path.join(self.source_folder, "LICENSE.txt"))
        bsd3 = re.search(r"==> Example License <==\n\n(.+?)\n==> ParU License <==", full_license_info, re.DOTALL).group(1)
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE.txt"), bsd3)

    def package(self):
        self._copy_license()
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "SuiteSparse_config")
        self.cpp_info.set_property("cmake_target_name", "SuiteSparse::SuiteSparseConfig")
        if not self.options.shared:
            self.cpp_info.set_property("cmake_target_aliases", ["SuiteSparse::SuiteSparseConfig_static"])
        self.cpp_info.set_property("pkg_config_name", "SuiteSparse_config")

        self.cpp_info.libs = ["suitesparseconfig"]
        self.cpp_info.includedirs.append(os.path.join("include", "suitesparse"))

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
