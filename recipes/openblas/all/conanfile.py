from os import path, environ
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches
from conan.tools.files import copy, get, load, rmdir, collect_libs
from conan.tools.scm import Version

required_conan_version = ">=1.55.0"


class OpenblasConan(ConanFile):
    name = "openblas"
    description = "An optimized BLAS library based on GotoBLAS2 1.13 BSD version"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.openblas.net"
    topics = ("blas", "lapack")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_lapack": [True, False],
        "use_thread": [True, False],
        "use_openmp": [True, False],
        "dynamic_arch": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_lapack": False,
        "use_thread": True,
        "use_openmp": False,
        "dynamic_arch": False,
    }
    package_type = "library"
    short_paths = True

    def _fortran_runtime(self, fortran_id):
        if self.settings.os in ["Linux", "FreeBSD"]:
            if fortran_id == "GNU":
                if self.settings.compiler == "gcc":
                    # Compiler vs. gfortran runtime ver.: 5,6: 3, 7: 4, >=8: 5
                    if Version(self.settings.compiler.version).major >= "5":
                        return "gfortran"
                if self.settings.compiler == "clang":
                    if Version(self.settings.compiler.version).major > "8":
                        return "gfortran"  # Runtime version gfortran5

        self.output.warning(
            f"Unable to select runtime for Fortran {fortran_id} "
            f"and C++ {self.settings.compiler} {self.settings.compiler.version}")
        return None

    @property
    def _openmp_runtime(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            if self.settings.compiler == "gcc":
                if Version(self.settings.compiler.version).major > "7":
                    return "gomp"
            if self.settings.compiler == "clang":
                if Version(self.settings.compiler.version).major > "8":
                    return "omp"
        return None

    @property
    def _fortran_compiler(self):
        comp_exe = self.conf.get("tools.build:compiler_executables")
        if comp_exe and 'fortran' in comp_exe:
            return comp_exe["fortran"]
        return environ.get('FC')

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        # Build LAPACK by default if possible w/o Fortran compiler
        if Version(self.version) >= "0.3.21":
            self.options.build_lapack = True

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        if self.info.options.build_lapack:
            # Capture fortran compiler in package id (if found)
            f_compiler = self._fortran_compiler
            if not f_compiler:
                self.output.warning("None or unknown fortran compiler was used.")
                f_compiler = True
            self.info.options.build_lapack = f_compiler

    def validate(self):
        if cross_building(self, skip_x64_x86=True):
            raise ConanInvalidConfiguration("Cross-building not implemented")

        if self.options.use_thread and self.options.use_openmp:
            raise ConanInvalidConfiguration("Both 'use_thread=True' and 'use_openmp=True' are not allowed")

        if self.settings.os == "Windows" and self.options.build_lapack and self.options.use_openmp:
            # In OpenBLAS cmake/system.cmake: Disable -fopenmp for LAPACK Fortran codes on Windows
            self.output.warning("OpenMP is disabled on LAPACK targets on Windows")

    def build_requirements(self):
        if self.options.build_lapack and self.settings.os == "Windows":
            self.tool_requires("ninja/1.11.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):

        ninja_generator = "Ninja" if self.settings.os == "Windows" and \
            self.options.build_lapack else None
        tc = CMakeToolchain(self, generator=ninja_generator)

        tc.variables["NOFORTRAN"] = not self.options.build_lapack
        if self.options.build_lapack:
            # This checks explicit user-specified fortran compiler
            if not self._fortran_compiler:
                if Version(self.version) < "0.3.21":
                    self.output.warning(
                        "Building with LAPACK support requires a Fortran compiler.")
                else:
                    tc.variables["C_LAPACK"] = True
                    tc.variables["NOFORTRAN"] = True
                    self.output.info(
                        "Building LAPACK without Fortran compiler")

        tc.variables["BUILD_WITHOUT_LAPACK"] = not self.options.build_lapack
        tc.variables["DYNAMIC_ARCH"] = self.options.dynamic_arch
        tc.variables["USE_THREAD"] = self.options.use_thread
        tc.variables["USE_OPENMP"] = self.options.use_openmp

        # Required for safe concurrent calls to OpenBLAS routines
        tc.variables["USE_LOCKING"] = not self.options.use_thread

        # don't, may lie to consumer, /MD or /MT is managed by conan
        tc.variables["MSVC_STATIC_CRT"] = False

        # Env variable escape hatch for enabling AVX512
        no_avx512 = environ.get("NO_AVX512")
        if no_avx512 is None:
            no_avx512 = True
        tc.variables["NO_AVX512"] = no_avx512

        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE",
             dst=path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, path.join(self.package_folder, "share"))

        if self.options.build_lapack:
            copy(self, pattern="FORTRAN_COMPILER",
                 src=self.build_folder,
                 dst=path.join(self.package_folder, "res"))

    def package_info(self):
        # CMake config file:
        # - OpenBLAS always has one and only one of these components: openmp, pthread or serial.
        # - Whether this component is requested or not, official CMake imported target is always OpenBLAS::OpenBLAS
        self.cpp_info.set_property("cmake_file_name", "OpenBLAS")
        self.cpp_info.set_property("cmake_target_name", "OpenBLAS::OpenBLAS")
        self.cpp_info.set_property("pkg_config_name", "openblas")

        component_name = "serial"
        if self.options.use_thread:
            component_name = "pthread"
        elif self.options.use_openmp:
            component_name = "openmp"

        self.cpp_info.components[component_name].set_property(
            "pkg_config_name", "openblas")

        # Target cannot be named pthread -> causes failed linking
        self.cpp_info.components[component_name].set_property(
            "cmake_target_name", "OpenBLAS::" + component_name)
        self.cpp_info.components[component_name].includedirs.append(
            path.join("include", "openblas")
        )
        self.cpp_info.components[component_name].libs = collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components[component_name].system_libs.append("m")
            if self.options.use_thread:
                self.cpp_info.components[component_name].system_libs.append("pthread")
            if self.options.use_openmp:
                openmp_rt = self._openmp_runtime
                if openmp_rt:
                    self.cpp_info.components[component_name].system_libs.append(openmp_rt)

        if self.options.build_lapack:
            fortran_file = path.join(self.package_folder, "res", "FORTRAN_COMPILER")
            # >=v0.3.21: compiling w/o fortran is possible
            if path.isfile(fortran_file):
                fortran_id = load(self, fortran_file)
                if fortran_id == "GNU":
                    fortran_rt = self._fortran_runtime(fortran_id)
                    if fortran_rt:
                        self.cpp_info.components[component_name].system_libs.append("dl")
                        self.cpp_info.components[component_name].system_libs.append(fortran_rt)
                elif fortran_id == "0":
                    pass
                else:
                    self.output.warning(f"Runtime libraries for {fortran_id} are not specified")

        self.cpp_info.requires.append(component_name)

        # TODO: Remove env_info in conan v2
        self.output.info(f"Setting OpenBLAS_HOME environment variable: {self.package_folder}")
        self.env_info.OpenBLAS_HOME = self.package_folder
        self.runenv_info.define_path("OpenBLAS_HOME", self.package_folder)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "OpenBLAS"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenBLAS"
        self.cpp_info.components[component_name].names["cmake_find_package"] = component_name
        self.cpp_info.components[component_name].names["cmake_find_package_multi"] = component_name
