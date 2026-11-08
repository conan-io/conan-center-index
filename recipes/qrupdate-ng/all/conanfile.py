from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
    rmdir,
)
import os

required_conan_version = ">=2.0.9"


class QrupdateConan(ConanFile):
    name = "qrupdate-ng"
    description = (
        "qrupdate-ng: a Fortran library for fast updates of QR and Cholesky decompositions "
        "(rank-1 updates, row/column insertion, deletion and shifts)."
    )
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.mpi-magdeburg.mpg.de/koehlerm/qrupdate-ng"
    topics = ("qr", "cholesky", "factorization", "linear-algebra", "fortran")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        # qrupdate needs LAPACK as well as BLAS
        "openblas/*:build_lapack": True,
    }
    implements = ["auto_shared_fpic"]

    @property
    def _fortran_compiler(self):
        # The Fortran compiler comes from the configuration: CMakeToolchain forwards it
        # to CMAKE_Fortran_COMPILER, so nothing has to be passed by hand
        comp_exe = self.conf.get("tools.build:compiler_executables")
        if comp_exe and "fortran" in comp_exe:
            return comp_exe["fortran"]

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        # The library is Fortran with a thin C interface: no C++ involved
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # OpenBLAS provides both BLAS and LAPACK (build_lapack=True is enforced in default_options and validate()).
        # The build discovers it through FindBLAS/FindLAPACK with BLA_VENDOR=OpenBLAS, see generate().
        self.requires("openblas/[>=0.3.24 <1]")

    def validate(self):
        if not self.dependencies["openblas"].options.build_lapack:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires LAPACK: set -o openblas/*:build_lapack=True"
            )

    def validate_build(self):
        if not self._fortran_compiler:
            # Only a suggestion, not a requirement: CMake still looks for a gfortran in the PATH
            self.output.warning(
                f"No Fortran compiler in the configuration and {self.ref} is written in Fortran. "
                "GCC provides gfortran, set it with "
                '-c tools.build:compiler_executables={"fortran": "gfortran"}'
            )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.20 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        deps = CMakeDeps(self)
        deps.set_property("openblas", "cmake_file_name", "BLAS")
        deps.set_property("openblas", "cmake_target_name", "BLAS::BLAS")
        deps.generate()

        tc = CMakeToolchain(self)
        tc.variables["CMAKE_TRY_COMPILE_CONFIGURATION"] = self.settings.build_type
        tc.cache_variables["BLA_VENDOR"] = "OpenBLAS"
        tc.cache_variables["BUILD_STATIC_LIBS"] = not self.options.shared
        tc.cache_variables["QRUPDATE_STATIC_WITH_PIC"] = bool(
            self.options.get_safe("fPIC", True)
        )
        tc.cache_variables["QRUPDATE_C_INTERFACE"] = True
        tc.cache_variables["QRUPDATE_DOCS"] = False
        tc.cache_variables["INTEGER8"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE",
            self.source_folder,
            os.path.join(self.package_folder, "licenses"),
        )
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "qrupdate")
        self.cpp_info.set_property("cmake_target_name", "qrupdate::qrupdate")
        self.cpp_info.set_property("pkg_config_name", "qrupdate")
        self.cpp_info.libs = ["qrupdate"]
        # C headers and Fortran modules (*.mod) are installed together
        self.cpp_info.includedirs = [os.path.join("include", "qrupdate")]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
        if not self.options.shared:
            self.cpp_info.defines.append("QRUPDATE_STATIC")
            # Fortran runtime. Like OpenBLAS, the consumer is responsible for making libgfortran
            # available to the linker (e.g. linking with the Fortran compiler of the configuration).
            self.cpp_info.system_libs.append("gfortran")
