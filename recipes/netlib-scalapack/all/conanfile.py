import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import get, copy

class NetlibScalapackConan(ConanFile):
    name = "netlib-scalapack"
    description = (
        "ScaLAPACK, or Scalable LAPACK, is a library of high performance linear"
        "algebra routines for distributed memory computers supporting MPI."
    )
    license = "BSD-3-Clause-Open-MPI"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Reference-ScaLAPACK/scalapack"
    topics = ("mpi", "HPC", "linear algebra")
    settings = "os", "arch", "build_type", "compiler"
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_intel_mpi": [True, False]
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "with_intel_mpi": False
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def validate(self):
        if self.settings.os not in ["Linux"]:
            raise ConanInvalidConfiguration("Only Linux is supported for now for this package.")

        if self.options.with_intel_mpi:
            i_mpi_root = VirtualBuildEnv(self).vars().get("I_MPI_ROOT")
            if not i_mpi_root:
                raise ConanInvalidConfiguration("when with_intel_mpi, you need to define I_MPI_ROOT in the buildenv section of your profile")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openblas/[~0.3]")
        if not self.options.with_intel_mpi:
            self.requires("openmpi/[~4]", options={"fortran": "yes"}, run=True)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.26]")
        if not self.options.with_intel_mpi:
            self.tool_requires("openmpi/[~4]", options={"fortran": "yes"})

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        vbe = VirtualBuildEnv(self)
        vbe.generate()
        
        tc = CMakeToolchain(self)
        tc.variables["LAPACK_FOUND"] = True

        blas = self.dependencies.get("openblas")
        if self.settings.os == "Linux":
            ext = ".so" if blas.options.get_safe("shared") else ".a"
        libdirs = blas.cpp_info.libdirs
        libs = blas.cpp_info.components["openblas_component"].libs
        blas_libs_full = ";".join(
            f"{d}/lib{lib}" + ext for d in libdirs for lib in libs
        )
        blas_include_dir = blas.cpp_info.includedir
        blas_libs = blas_libs_full
        lapack_libs = blas_libs_full

        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["BUILD_STATIC_LIBS"] = not self.options.shared

        tc.variables["LAPACK_INCLUDE_DIRS"] = blas_include_dir
        tc.variables["LAPACK_LIBRARIES"] = lapack_libs
        tc.variables["BLAS_LIBRARIES"] = blas_libs

        # https://bugzilla.redhat.com/show_bug.cgi?id=2178710
        tc.extra_cflags = ["-std=gnu89"]
        tc.generate()

        deps = CMakeDeps(self)
        if not self.options.with_intel_mpi:
            deps.set_property("openmpi", "cmake_find_mode", "none")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["scalapack"]
        self.cpp_info.includedirs = []
