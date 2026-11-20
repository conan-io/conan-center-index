from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
    rmdir,
)
import os
import shutil

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
        # 1. Explicitly configured Fortran compiler
        comp_exe = self.conf.get(
            "tools.build:compiler_executables", default={}, check_type=dict
        )
        if comp_exe.get("fortran"):
            return comp_exe["fortran"]
        # 2. A gfortran available in the system
        return shutil.which("gfortran")

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
        # See patches/0001-use-openblas-and-skip-tests.patch
        self.requires("openblas/[>=0.3.24 <1]")

    def validate(self):
        if not self.dependencies["openblas"].options.build_lapack:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires LAPACK: set -o openblas/*:build_lapack=True"
            )

    def validate_build(self):
        if self.settings.os == "Windows" and not self._fortran_compiler:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires a Fortran compiler. "
                'Set it with -c tools.build:compiler_executables={"fortran": "<path to gfortran>"}'
            )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.20 <4]")
        if not self._fortran_compiler:
            # No Fortran compiler available: fallback to the (slow to build) gcc package.
            self.tool_requires("gcc/[>=11]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def _gcc_fortran_compiler(self):
        gcc = self.dependencies.build["gcc"]
        return os.path.join(gcc.package_folder, "bin", f"gfortran-{gcc.ref.version}")

    def generate(self):
        env = VirtualBuildEnv(self)
        if not self._fortran_compiler:
            # Use the gcc package only for Fortran: keep the C compiler of the profile.
            buildenv = env.environment()
            for var in ("CC", "CXX", "AR", "NM", "RANLIB"):
                buildenv.unset(var)
        env.generate()

        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_Fortran_COMPILER"] = (
            self._fortran_compiler or self._gcc_fortran_compiler()
        )
        # The upstream CMakeLists builds both flavours by default: only build the requested one
        tc.cache_variables["BUILD_STATIC_LIBS"] = not self.options.shared
        tc.cache_variables["QRUPDATE_STATIC_WITH_PIC"] = bool(
            self.options.get_safe("fPIC", True)
        )
        tc.cache_variables["QRUPDATE_C_INTERFACE"] = True
        tc.cache_variables["QRUPDATE_DOCS"] = False
        tc.cache_variables["INTEGER8"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

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
            # findable by the linker (e.g. -L<gfortran lib dir> in tools.build:exelinkflags).
            self.cpp_info.system_libs.append("gfortran")
