from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir, collect_libs
from conan.tools.build import cross_building
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os
import functools

required_conan_version = ">=1.53.0"


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
        "dynamic_arch": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_lapack": False,
        "use_thread": True,
        "dynamic_arch": False,
    }
    short_paths = True

    def export_sources(self):
       copy(self, "CMakeLists.txt", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def validate(self):
        if hasattr(self, "settings_build") and cross_building(self, skip_x64_x86=True):
            raise ConanInvalidConfiguration("Cross-building not implemented")

    def source(self):
        get(self,
            **self.conan_data["sources"][self.version],
            strip_root=True,
            destination=self.source_folder
        )

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)

        if self.options.build_lapack:
            self.output.warn("Building with lapack support requires a Fortran compiler.")
        tc.variables["NOFORTRAN"] = not self.options.build_lapack
        tc.variables["BUILD_WITHOUT_LAPACK"] = not self.options.build_lapack
        tc.variables["DYNAMIC_ARCH"] = self.options.dynamic_arch
        tc.variables["USE_THREAD"] = self.options.use_thread

        # Required for safe concurrent calls to OpenBLAS routines
        tc.variables["USE_LOCKING"] = not self.options.use_thread

        tc.variables[
            "MSVC_STATIC_CRT"
        ] = False  # don't, may lie to consumer, /MD or /MT is managed by conan

        # This is a workaround to add the libm dependency on linux,
        # which is required to successfully compile on older gcc versions.
        tc.variables["ANDROID"] = self.settings.os in ["Linux", "Android"]

        tc.generate()

    def build(self):
        if Version(self.version) >= "0.3.12":
            search = """message(STATUS "No Fortran compiler found, can build only BLAS but not LAPACK")"""
            replace = (
                """message(FATAL_ERROR "No Fortran compiler found. Cannot build with LAPACK.")"""
            )
        else:
            search = "enable_language(Fortran)"
            replace = """include(CheckLanguage)
check_language(Fortran)
if(CMAKE_Fortran_COMPILER)
  enable_language(Fortran)
else()
  message(FATAL_ERROR "No Fortran compiler found. Cannot build with LAPACK.")
  set (NOFORTRAN 1)
  set (NO_LAPACK 1)
endif()"""

        replace_in_file(self,
            os.path.join(self.source_folder, self.source_folder, "cmake", "f_check.cmake"),
            search,
            replace,
        )
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = self._configure_cmake()
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        # CMake config file:
        # - OpenBLAS always has one and only one of these components: openmp, pthread or serial.
        # - Whatever if this component is requested or not, official CMake imported target is always OpenBLAS::OpenBLAS
        # - TODO: add openmp component when implemented in this recipe
        self.cpp_info.set_property("cmake_file_name", "OpenBLAS")
        self.cpp_info.set_property("cmake_target_name", "OpenBLAS::OpenBLAS")
        self.cpp_info.set_property("pkg_config_name", "openblas")
        cmake_component_name = "pthread" if self.options.use_thread else "serial" # TODO: ow to model this in CMakeDeps?
        self.cpp_info.components["openblas_component"].set_property("pkg_config_name", "openblas")
        self.cpp_info.components["openblas_component"].includedirs.append(
            os.path.join("include", "openblas")
        )
        self.cpp_info.components["openblas_component"].libs = collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["openblas_component"].system_libs.append("m")
            if self.options.use_thread:
                self.cpp_info.components["openblas_component"].system_libs.append("pthread")
            if self.options.build_lapack:
                self.cpp_info.components["openblas_component"].system_libs.append("gfortran")

        self.output.info(
            "Setting OpenBLAS_HOME environment variable: {}".format(self.package_folder)
        )
        self.env_info.OpenBLAS_HOME = self.package_folder

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "OpenBLAS"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenBLAS"
        self.cpp_info.components["openblas_component"].names["cmake_find_package"] = cmake_component_name
        self.cpp_info.components["openblas_component"].names["cmake_find_package_multi"] = cmake_component_name
