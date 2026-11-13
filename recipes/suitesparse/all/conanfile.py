import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir

required_conan_version = ">=2.4"


class SuiteSparseConan(ConanFile):
    name = "suitesparse"
    description = "A suite of sparse matrix algorithms"
    license = (
        "BSD-2-Clause",
        "BSD-3-Clause",
        "LGPL-2.1-or-later",
        "GPL-2.0-or-later",
        "GPL-3.0-or-later",
        "Apache-2.0",
    )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/DrTimothyAldenDavis/SuiteSparse"
    topics = ("sparse-matrix", "linear-algebra", "solver", "graph-algorithms")
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openmp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openmp": False,
    }

    # all libraries built from the single upstream monorepo
    _packages = (
        "SuiteSparse_config", "Mongoose", "AMD", "BTF", "CAMD", "CCOLAMD",
        "COLAMD", "CXSparse", "LDL", "KLU", "UMFPACK", "CHOLMOD", "RBio",
        "SPQR", "SPEX", "ParU", "GraphBLAS", "LAGraph",
    )

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Macos":
            # no OpenMP runtime available for apple-clang
            del self.options.with_openmp
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.options["openblas"].build_lapack = True

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires("openblas/0.3.30")
        # GMP and MPFR are required by SPEX
        self.requires("gmp/6.3.0", transitive_headers=True, transitive_libs=True)
        self.requires("mpfr/4.2.2", transitive_headers=True, transitive_libs=True)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.23 <4]")
        self.tool_requires("ninja/[>=1.10 <2]")

    def validate(self):
        # ParU is C++, GraphBLAS JIT-compiled code expects a modern compiler
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][str(self.version)], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()
        CMakeDeps(self).generate()
        tc = CMakeToolchain(self)

        tc.cache_variables["BLA_VENDOR"] = "OpenBLAS"

        tc.cache_variables["BUILD_STATIC_LIBS"] = not self.options.shared
        tc.cache_variables["GRAPHBLAS_BUILD_STATIC_LIBS"] = not self.options.shared
        tc.cache_variables["GRAPHBLAS_USE_JIT"] = False
        tc.cache_variables["SUITESPARSE_USE_CUDA"] = False
        tc.cache_variables["SUITESPARSE_USE_PYTHON"] = False
        tc.cache_variables["SUITESPARSE_USE_FORTRAN"] = False
        tc.cache_variables["SUITESPARSE_DEMOS"] = False
        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["SUITESPARSE_USE_OPENMP"] = bool(self.options.get_safe("with_openmp", False))
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        licenses_folder = os.path.join(self.package_folder, "licenses")
        copy(self, "LICENSE.txt", self.source_folder, licenses_folder)
        for package in self._packages:
            copy(self, "License.txt", os.path.join(self.source_folder, package, "Doc"), licenses_folder)
            copy(self, "LICENSE*", os.path.join(self.source_folder, package), licenses_folder)
        # remove upstream CMake package-config and pkg-config files:
        # CMakeDeps and PkgConfigDeps generate their own from the components below
        for folder in ("lib/cmake", "lib/pkgconfig", "share"):
            rmdir(self, os.path.join(self.package_folder, folder))

    def package_info(self):
        # all SuiteSparse headers are installed into include/suitesparse
        self.cpp_info.includedirs = [os.path.join("include", "suitesparse")]
        self.cpp_info.set_property("cmake_file_name", "SuiteSparse")

        # component name: (libs, requires, pkg-config name)
        # library names as installed by the upstream CMake install step
        components = {
            "suitesparse_config": (["suitesparseconfig"], [], "SuiteSparse_config"),
            "amd": (["amd"], ["suitesparse_config"], "AMD"),
            "btf": (["btf"], ["suitesparse_config"], "BTF"),
            "camd": (["camd"], ["suitesparse_config"], "CAMD"),
            "ccolamd": (["ccolamd"], ["suitesparse_config"], "CCOLAMD"),
            "colamd": (["colamd"], ["suitesparse_config"], "COLAMD"),
            "cxsparse": (["cxsparse"], ["suitesparse_config"], "CXSparse"),
            "ldl": (["ldl"], ["suitesparse_config", "amd"], "LDL"),
            "mongoose": (["suitesparse_mongoose"], ["suitesparse_config"], "SuiteSparse_Mongoose"),
            "klu": (["klu"], ["suitesparse_config", "btf", "amd"], "KLU"),
            "klu_cholmod": (["klu_cholmod"], ["klu", "cholmod"], "KLU_CHOLMOD"),
            "umfpack": (["umfpack"], ["suitesparse_config", "amd", "colamd", "cholmod", "openblas::openblas_component"], "UMFPACK"),
            "cholmod": (["cholmod"], ["suitesparse_config", "amd", "camd", "ccolamd", "colamd", "openblas::openblas_component"], "CHOLMOD"),
            "rbio": (["rbio"], ["suitesparse_config", "cholmod"], "RBio"),
            "spqr": (["spqr"], ["suitesparse_config", "cholmod", "openblas::openblas_component"], "SPQR"),
            "spex": (["spex"], ["suitesparse_config", "amd", "colamd", "gmp::gmp", "mpfr::mpfr"], "SPEX"),
            "paru": (["paru"], ["suitesparse_config", "umfpack", "cholmod", "openblas::openblas_component"], "ParU"),
            "graphblas": (["graphblas"], [], "GraphBLAS"),
            # LAGraph also installs the experimental liblagraphx
            "lagraph": (["lagraph", "lagraphx"], ["suitesparse_config", "graphblas"], "LAGraph"),
        }
        # cmake target name per component, e.g. SuiteSparse::CHOLMOD
        cmake_targets = {
            "suitesparse_config": "SuiteSparseConfig",
            "amd": "AMD", "btf": "BTF", "camd": "CAMD", "ccolamd": "CCOLAMD",
            "colamd": "COLAMD", "cxsparse": "CXSparse", "ldl": "LDL",
            "mongoose": "Mongoose", "klu": "KLU", "klu_cholmod": "KLU_CHOLMOD",
            "umfpack": "UMFPACK", "cholmod": "CHOLMOD", "rbio": "RBio",
            "spqr": "SPQR", "spex": "SPEX", "paru": "ParU",
            "graphblas": "GraphBLAS", "lagraph": "LAGraph",
        }
        for name, (libs, requires, pkg_config) in components.items():
            component = self.cpp_info.components[name]
            component.libs = libs
            component.includedirs = [os.path.join("include", "suitesparse")]
            component.set_property("cmake_target_name", f"SuiteSparse::{cmake_targets[name]}")
            component.set_property("pkg_config_name", pkg_config)
            if requires:
                component.requires = requires
