from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir, collect_libs
from conan.tools.build import cross_building
from conan.tools.scm import Version
from conan.tools.apple import fix_apple_shared_install_name
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
    package_type = "library"

    @property
    def _fortran_compiler(self):
        comp_exe = self.conf.get("tools.build:compiler_executables")
        if comp_exe and 'fortran' in comp_exe:
            return comp_exe["fortran"]
        return None

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) >= "0.3.21":
            # INFO: When no Fortran compiler is available, OpenBLAS builds LAPACK from an f2c-converted copy of LAPACK unless the NO_LAPACK option is specified
            self.options.build_lapack = True

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def validate(self):
        if Version(self.version) < "0.3.24" and self.settings.arch == "armv8":
            # OpenBLAS fails to detect the appropriate target architecture for armv8 for versions < 0.3.24, as it matches the 32 bit variant instead of 64.
            # This was fixed in https://github.com/OpenMathLib/OpenBLAS/pull/4142, which was introduced in 0.3.24.
            # This would be a reasonably trivial hotfix to backport.
            raise ConanInvalidConfiguration("armv8 builds are not currently supported for versions lower than 0.3.24. Contributions to support this are welcome.")

        if hasattr(self, "settings_build") and cross_building(self, skip_x64_x86=True):
            raise ConanInvalidConfiguration("Cross-building not implemented")

    def source(self):
        get(self,
            **self.conan_data["sources"][self.version],
            strip_root=True,
            destination=self.source_folder
        )

        if Version(self.version) <= "0.3.15":
            replace_in_file(self, os.path.join(self.source_folder, "cmake", "utils.cmake"),
                            "set(obj_defines ${defines_in})", "set(obj_defines ${defines_in})\r\n\r\n" +
                            "list(FIND obj_defines \"RC\" def_idx)\r\n" + "if (${def_idx} GREATER -1) \r\n\t" +
                            "list (REMOVE_ITEM obj_defines \"RC\")\r\n\t" + "list(APPEND obj_defines  \"RC=RC\")\r\n" +
                            "endif ()\r\n" + "list(FIND obj_defines \"CR\" def_idx)\r\n" +
                            "if (${def_idx} GREATER -1) \r\n\t" + "list (REMOVE_ITEM obj_defines \"CR\")\r\n\t" +
                            "list(APPEND obj_defines  \"CR=CR\")\r\n" + "endif ()")

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)

        tc.cache_variables["NOFORTRAN"] = not self.options.build_lapack
        # This checks explicit user-specified fortran compiler
        if self.options.build_lapack:
            if not self._fortran_compiler:
                if Version(self.version) < "0.3.21":
                    self.output.warning(
                        "Building with LAPACK support requires a Fortran compiler.")
                else:
                    tc.cache_variables["C_LAPACK"] = True
                    tc.cache_variables["NOFORTRAN"] = True
                    self.output.info(
                        "Building LAPACK without Fortran compiler")

        tc.cache_variables["BUILD_WITHOUT_LAPACK"] = not self.options.build_lapack
        tc.cache_variables["DYNAMIC_ARCH"] = self.options.dynamic_arch
        tc.cache_variables["USE_THREAD"] = self.options.use_thread

        # Required for safe concurrent calls to OpenBLAS routines
        tc.cache_variables["USE_LOCKING"] = not self.options.use_thread

        # don't, may lie to consumer, /MD or /MT is managed by conan
        tc.cache_variables["MSVC_STATIC_CRT"] = False

        # This is a workaround to add the libm dependency on linux,
        # which is required to successfully compile on older gcc versions.
        tc.cache_variables["ANDROID"] = self.settings.os in ["Linux", "Android"]

        tc.generate()

    def build(self):
        if Version(self.version) < "0.3.21":
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

            replace_in_file(
                self,
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
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        # CMake config file:
        # - OpenBLAS always has one and only one of these components: openmp, pthread or serial.
        # - Whatever if this component is requested or not, official CMake imported target is always OpenBLAS::OpenBLAS
        # - TODO: add openmp component when implemented in this recipe
        self.cpp_info.set_property("cmake_file_name", "OpenBLAS")
        self.cpp_info.set_property("cmake_target_name", "OpenBLAS::OpenBLAS")
        self.cpp_info.set_property("pkg_config_name", "openblas")
        cmake_component_name = "pthread" if self.options.use_thread else "serial"  # TODO: how to model this in CMakeDeps?
        self.cpp_info.components["openblas_component"].set_property(
            "cmake_target_name", "OpenBLAS::" + cmake_component_name)  # 'pthread' causes issues without namespace
        self.cpp_info.components["openblas_component"].set_property("pkg_config_name", "openblas")
        self.cpp_info.components["openblas_component"].includedirs.append(
            os.path.join("include", "openblas")
        )
        self.cpp_info.components["openblas_component"].libs = collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["openblas_component"].system_libs.append("m")
            if self.options.use_thread:
                self.cpp_info.components["openblas_component"].system_libs.append("pthread")
            if self.options.build_lapack and self._fortran_compiler:
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
