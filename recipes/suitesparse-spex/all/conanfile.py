import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import get, rm, rmdir, copy, export_conandata_patches, apply_conandata_patches

required_conan_version = ">=1.53.0"


class SuiteSparseSpexConan(ConanFile):
    name = "suitesparse-spex"
    description = "SPEX: Software package for SParse EXact algebra in SuiteSparse"
    license = "GPL-2.0-or-later or LGPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://people.engr.tamu.edu/davis/suitesparse.html"
    topics = ("mathematics", "sparse-matrix", "linear-algebra", "exact-linear-algebra")

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

    def export_sources(self):
        export_conandata_patches(self)

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
        # OpenBLAS and OpenMP are provided via suitesparse-config
        self.requires("suitesparse-config/7.7.0", transitive_headers=True, transitive_libs=True)
        self.requires("suitesparse-amd/3.3.2")
        self.requires("suitesparse-colamd/3.3.3")
        # https://github.com/DrTimothyAldenDavis/SuiteSparse/blob/v7.7.0/SPEX/Include/SPEX.h#L96-L97
        self.requires("gmp/6.3.0", transitive_headers=True, transitive_libs=True)
        self.requires("mpfr/4.2.1", transitive_headers=True, transitive_libs=True)

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
        tc.variables["SUITESPARSE_DEMOS"] = False
        tc.variables["SUITESPARSE_USE_FORTRAN"] = False  # Fortran sources are translated to C instead
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "SPEX"))
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", os.path.join(self.source_folder, "SPEX"), os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "SPEX")
        self.cpp_info.set_property("cmake_target_name", "SuiteSparse::SPEX")
        if not self.options.shared:
            self.cpp_info.set_property("cmake_target_aliases", ["SuiteSparse::COLAMD_static"])
        self.cpp_info.set_property("pkg_config_name", "SPEX")

        self.cpp_info.libs = ["spex"]
        self.cpp_info.includedirs.append(os.path.join("include", "suitesparse"))

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
