import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import get, rm, rmdir, copy, save

required_conan_version = ">=1.53.0"


class SuiteSparseCholmodConan(ConanFile):
    name = "suitesparse-cholmod"
    description = "CHOLMOD: Routines for factorizing sparse symmetric positive definite matrices in SuiteSparse"
    license = "LGPL-2.1-or-later AND GPL-2.0-or-later AND Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://people.engr.tamu.edu/davis/suitesparse.html"
    topics = ("mathematics", "sparse-matrix", "linear-algebra", "matrix-factorization")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "gpl": [True, False],
        "cuda": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "gpl": True,
        "cuda": False,
    }
    options_description = {
        "gpl": "Enable GPL-licensed modules: MatrixOps, Modify, Supernodal and CUDA",
        "cuda": "Enable CUDA acceleration",
    }

    def export_sources(self):
        copy(self, "cholmod-conan-cuda-support.cmake", self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def package_id(self):
        if not self.info.options.gpl:
            self.license = "LGPL-2.1-or-later AND Apache-2.0"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # OpenBLAS and OpenMP are provided via suitesparse-config
        self.requires("suitesparse-config/7.7.0", transitive_headers=True, transitive_libs=True)
        self.requires("suitesparse-amd/3.3.2")
        self.requires("suitesparse-camd/3.3.2")
        self.requires("suitesparse-colamd/3.3.3")
        self.requires("suitesparse-ccolamd/3.3.3")

        # A modified vendored version of METIS v5.1.0 is included,
        # but it has been modified to not conflict with the general version

    def validate(self):
        if self.options.cuda and not self.options.gpl:
            raise ConanInvalidConfiguration("CUDA acceleration requires GPL-licensed modules. Set suitesparse-cholmod/*:gpl=True.")

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
        tc.variables["CHOLMOD_GPL"] = self.options.gpl
        tc.variables["SUITESPARSE_USE_OPENMP"] = True
        tc.variables["SUITESPARSE_USE_CUDA"] = self.options.cuda
        tc.variables["SUITESPARSE_DEMOS"] = False
        tc.variables["SUITESPARSE_USE_FORTRAN"] = False  # Fortran sources are translated to C instead
        # FIXME: Find a way to not hardcode this. The system BLAS gets used otherwise.
        tc.variables["BLAS_LIBRARIES"] = "OpenBLAS::OpenBLAS"
        tc.variables["LAPACK_LIBRARIES"] = "OpenBLAS::OpenBLAS"
        tc.variables["LAPACK_FOUND"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "CHOLMOD"))
        cmake.build()

    def package(self):
        copy(self, "License.txt", os.path.join(self.source_folder, "CHOLMOD", "Doc"), os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)
        if self.options.cuda:
            copy(self, "cholmod-conan-cuda-support.cmake", self.export_sources_folder, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CHOLMOD")
        self.cpp_info.set_property("cmake_target_name", "SuiteSparse::CHOLMOD")
        if not self.options.shared:
            self.cpp_info.set_property("cmake_target_aliases", ["SuiteSparse::CHOLMOD_static"])
        self.cpp_info.set_property("pkg_config_name", "CHOLMOD")

        if self.options.cuda:
            self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))
            self.cpp_info.set_property("cmake_build_modules", [os.path.join("lib", "cmake", "cholmod-conan-cuda-support.cmake")])

        self.cpp_info.libs = ["cholmod"]
        self.cpp_info.includedirs.append(os.path.join("include", "suitesparse"))

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        if not self.options.gpl:
            self.cpp_info.defines.append("NGPL")
        if self.options.cuda:
            self.cpp_info.defines.append("CHOLMOD_HAS_CUDA")
