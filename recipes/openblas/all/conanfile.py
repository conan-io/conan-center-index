from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class OpenblasConan(ConanFile):
    name = "openblas"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.openblas.net"
    description = "An optimized BLAS library based on GotoBLAS2 1.13 BSD version"
    topics = ("openblas", "blas", "lapack")
    settings = "os", "compiler", "build_type", "arch"
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
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    _cmake = None
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if hasattr(self, "settings_build") and tools.cross_building(self, skip_x64_x86=True):
            raise ConanInvalidConfiguration("Cross-building not implemented")

    def source(self):
        tools.get(
            **self.conan_data["sources"][self.version],
            strip_root=True,
            destination=self._source_subfolder
        )

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        if self.options.build_lapack:
            self.output.warn("Building with lapack support requires a Fortran compiler.")
        self._cmake.definitions["NOFORTRAN"] = not self.options.build_lapack
        self._cmake.definitions["BUILD_WITHOUT_LAPACK"] = not self.options.build_lapack
        self._cmake.definitions["DYNAMIC_ARCH"] = self.options.dynamic_arch
        self._cmake.definitions["USE_THREAD"] = self.options.use_thread

        # Required for safe concurrent calls to OpenBLAS routines
        self._cmake.definitions["USE_LOCKING"] = not self.options.use_thread

        self._cmake.definitions[
            "MSVC_STATIC_CRT"
        ] = False  # don't, may lie to consumer, /MD or /MT is managed by conan

        # This is a workaround to add the libm dependency on linux,
        # which is required to successfully compile on older gcc versions.
        self._cmake.definitions["ANDROID"] = self.settings.os in ["Linux", "Android"]

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        if tools.Version(self.version) >= "0.3.12":
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

        tools.replace_in_file(
            os.path.join(self._source_subfolder, "cmake", "f_check.cmake"),
            search,
            replace,
        )
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        # CMake config file:
        # - OpenBLAS always has one and only one of these components: openmp, pthread or serial.
        # - Whatever if this component is requested or not, official CMake imported target is always OpenBLAS::OpenBLAS
        # - TODO: add openmp component when implemented in this recipe
        self.cpp_info.names["cmake_find_package"] = "OpenBLAS"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenBLAS"
        self.cpp_info.names["pkg_config"] = "openblas"
        cmake_component_name = "pthread" if self.options.use_thread else "serial"
        self.cpp_info.components["openblas_component"].names[
            "cmake_find_package"
        ] = cmake_component_name
        self.cpp_info.components["openblas_component"].names[
            "cmake_find_package_multi"
        ] = cmake_component_name
        self.cpp_info.components["openblas_component"].names["pkg_config"] = "openblas"
        self.cpp_info.components["openblas_component"].includedirs.append(
            os.path.join("include", "openblas")
        )
        self.cpp_info.components["openblas_component"].libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            if self.options.use_thread:
                self.cpp_info.components["openblas_component"].system_libs.append("pthread")
            if self.options.build_lapack:
                self.cpp_info.components["openblas_component"].system_libs.append("gfortran")

        self.output.info(
            "Setting OpenBLAS_HOME environment variable: {}".format(self.package_folder)
        )
        self.env_info.OpenBLAS_HOME = self.package_folder
