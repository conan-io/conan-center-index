import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import get, rm, rmdir, copy

required_conan_version = ">=1.53.0"


class SuiteSparseKluConan(ConanFile):
    name = "suitesparse-klu"
    description = "KLU: Routines for solving sparse linear systems of equations in SuiteSparse"
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://people.engr.tamu.edu/davis/suitesparse.html"
    topics = ("mathematics", "sparse-matrix", "linear-algebra", "linear-systems-solver")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_cholmod": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_cholmod": True,
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
        # OpenBLAS and OpenMP are provided via suitesparse-config
        self.requires("suitesparse-config/7.7.0", transitive_headers=True, transitive_libs=True)
        self.requires("suitesparse-amd/3.3.2", transitive_headers=True, transitive_libs=True)
        self.requires("suitesparse-btf/2.3.2", transitive_headers=True, transitive_libs=True)
        self.requires("suitesparse-colamd/3.3.3", transitive_headers=True, transitive_libs=True)
        if self.options.with_cholmod:
            self.requires("suitesparse-cholmod/5.2.1", transitive_headers=True, transitive_libs=True)

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
        tc.variables["KLU_USE_CHOLMOD"] = self.options.with_cholmod
        tc.variables["SUITESPARSE_USE_OPENMP"] = True
        tc.variables["SUITESPARSE_USE_CUDA"] = False
        tc.variables["SUITESPARSE_DEMOS"] = False
        tc.variables["SUITESPARSE_USE_FORTRAN"] = False  # Fortran sources are translated to C instead
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "KLU"))
        cmake.build()

    def package(self):
        copy(self, "License.txt", os.path.join(self.source_folder, "KLU", "Doc"), os.path.join(self.package_folder, "licenses"))
        copy(self, "lesser.txt", os.path.join(self.source_folder, "KLU", "Doc"), os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "KLU")

        self.cpp_info.components["KLU"].libs = ["klu"]
        self.cpp_info.components["KLU"].set_property("cmake_target_name", "SuiteSparse::KLU")
        if not self.options.shared:
            self.cpp_info.components["KLU"].set_property("cmake_target_aliases", ["SuiteSparse::KLU_static"])
        self.cpp_info.components["KLU"].set_property("pkg_config_name", "KLU")
        self.cpp_info.components["KLU"].includedirs.append(os.path.join("include", "suitesparse"))
        self.cpp_info.components["KLU"].requires = [
            "suitesparse-config::suitesparse-config",
            "suitesparse-amd::suitesparse-amd",
            "suitesparse-btf::suitesparse-btf",
            "suitesparse-colamd::suitesparse-colamd",
        ]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["KLU"].system_libs.append("m")

        if self.options.with_cholmod:
            self.cpp_info.components["KLU_CHOLMOD"].libs = ["klu_cholmod"]
            self.cpp_info.components["KLU_CHOLMOD"].set_property("cmake_target_name", "SuiteSparse::KLU_CHOLMOD")
            if not self.options.shared:
                self.cpp_info.components["KLU"].set_property("cmake_target_aliases", ["SuiteSparse::KLU_CHOLMOD_static"])
            self.cpp_info.components["KLU_CHOLMOD"].set_property("pkg_config_name", "KLU_CHOLMOD")
            self.cpp_info.components["KLU_CHOLMOD"].includedirs.append(os.path.join("include", "suitesparse"))
            self.cpp_info.components["KLU_CHOLMOD"].requires = [
                "KLU",
                "suitesparse-cholmod::suitesparse-cholmod",
            ]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["KLU_CHOLMOD"].system_libs.append("m")
