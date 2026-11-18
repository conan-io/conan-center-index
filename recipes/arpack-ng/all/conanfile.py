from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.gnu import PkgConfigDeps
from conan.tools.files import (
    copy,
    export_conandata_patches,
    get,
    rmdir,
)
import os

required_conan_version = ">=2.0.9"


class ArpackNgConan(ConanFile):
    name = "arpack-ng"
    description = (
        "ARPACK-NG is a collection of Fortran77 subroutines designed to solve "
        "large scale eigenvalue problems."
    )
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/opencollab/arpack-ng"
    topics = (
        "eigenvalue",
        "eigenvector",
        "arnoldi",
        "lanczos",
        "fortran",
        "linear-algebra",
    )
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "icb": [True, False],
        "eigen": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "icb": True,
        "eigen": True,
        "openblas/*:build_lapack": True,
    }
    options_description = {
        "icb": "Install the C/C++ headers (arpack.h, arpack.hpp) based on ISO_C_BINDING for the *[ae]upd_c functions",
        "eigen": "Install arpackSolver.hpp, an eigenvalue-problems solver based on ICB and Eigen (requires icb)",
    }
    implements = ["auto_shared_fpic"]

    @property
    def _fortran_compiler(self):
        return self.conf.get(
            "tools.build:compiler_executables", default={}, check_type=dict
        ).get("fortran")

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires(
            "openblas/[>=0.3.24 <1]", transitive_headers=True, transitive_libs=True
        )
        if self.options.eigen:
            self.requires("eigen/[>=3.3 <6]", transitive_headers=True)

    def validate(self):
        if self.options.eigen and not self.options.icb:
            raise ConanInvalidConfiguration(
                f"-o {self.name}/*:eigen=True requires -o {self.name}/*:icb=True"
            )
        if not self.dependencies["openblas"].options.build_lapack:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires LAPACK: set -o openblas/*:build_lapack=True"
            )

    def validate_build(self):
        if not self._fortran_compiler:
            raise ConanInvalidConfiguration(
                f"{self.ref} needs a Fortran compiler: set it in the profile, e.g. "
                'tools.build:compiler_executables={"fortran": "gfortran"}'
            )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.19 <4]")
        self.tool_requires("pkgconf/[>=2.2 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_Fortran_COMPILER"] = self._fortran_compiler
        tc.cache_variables["TESTS"] = False
        tc.cache_variables["EXAMPLES"] = False
        tc.cache_variables["MPI"] = False
        tc.cache_variables["PYTHON3"] = False
        tc.cache_variables["EIGEN"] = bool(self.options.eigen)
        tc.cache_variables["ICB"] = bool(self.options.icb)
        tc.cache_variables["INTERFACE64"] = False
        tc.generate()

        # Eigen and OpenBLAS are resolved via cmake via pkgconfig
        pkg_config_deps = PkgConfigDeps(self)
        pkg_config_deps.set_property(
            "openblas", "pkg_config_aliases", ["blas", "lapack"]
        )
        pkg_config_deps.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "COPYING",
            self.source_folder,
            os.path.join(self.package_folder, "licenses"),
        )
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "arpackng")
        self.cpp_info.set_property("cmake_target_name", "ARPACK::ARPACK")
        self.cpp_info.set_property("pkg_config_name", "arpack")
        self.cpp_info.libs = ["arpack"]
        self.cpp_info.includedirs = ["include", os.path.join("include", "arpack")]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
        if not self.options.shared and is_apple_os(self):
            # Apple's linker deduplication breaks the static OpenBLAS assembly kernels (segfault in dcopy_k)
            self.cpp_info.exelinkflags.append("-Wl,-no_deduplicate")
        if not self.options.shared:
            # Fortran runtime. Like OpenBLAS, the consumer is responsible for making libgfortran
            # findable by the linker (e.g. -L<gfortran lib dir> in tools.build:exelinkflags).
            self.cpp_info.system_libs.append("gfortran")
