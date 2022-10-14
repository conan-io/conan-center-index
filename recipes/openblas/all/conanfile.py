from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake
from conan.tools import build
from conan.tools.scm import Version
from conan.tools.files import get, replace_in_file, rmdir, collect_libs
import os
import functools

required_conan_version = ">=1.43.0"

# Copypasting here content of OpenBlas/TargetList.txt
# https://github.com/xianyi/OpenBLAS/blob/develop/TargetList.txt
# https://github.com/xianyi/OpenBLAS#normal-compile
openblas_target_list = [
        "native", # We rely on architecture detection in OpenBlas cmake scripts

        # 1.X86/X86_64
        # a)Intel CPU:
        "P2",
        "KATMAI",
        "COPPERMINE",
        "NORTHWOOD",
        "PRESCOTT",
        "BANIAS",
        "YONAH",
        "CORE2",
        "PENRYN",
        "DUNNINGTON",
        "NEHALEM",
        "SANDYBRIDGE",
        "HASWELL",
        "SKYLAKEX",
        "ATOM",
        "COOPERLAKE",
        "SAPPHIRERAPIDS",

        # b)AMD CPU:
        "ATHLON",
        "OPTERON",
        "OPTERON_SSE3",
        "BARCELONA",
        "SHANGHAI",
        "ISTANBUL",
        "BOBCAT",
        "BULLDOZER",
        "PILEDRIVER",
        "STEAMROLLER",
        "EXCAVATOR",
        "ZEN",

        # c)VIA CPU:
        "SSE_GENERIC",
        "VIAC3",
        "NANO",

        # 2.Power CPU:
        "POWER4",
        "POWER5",
        "POWER6",
        "POWER7",
        "POWER8",
        "POWER9",
        "POWER10",
        "PPCG4",
        "PPC970",
        "PPC970MP",
        "PPC440",
        "PPC440FP2",
        "CELL",

        # 3.MIPS CPU:
        "P5600",
        "MIPS1004K",
        "MIPS24K",

        # 4.MIPS64 CPU:
        "MIPS64_GENERIC",
        "SICORTEX",
        "LOONGSON3A",
        "LOONGSON3B",
        "I6400",
        "P6600",
        "I6500",

        # 5.IA64 CPU:
        "ITANIUM2",

        # 6.SPARC CPU:
        "SPARC",
        "SPARCV7",

        # 7.ARM CPU:
        "CORTEXA15",
        "CORTEXA9",
        "ARMV7",
        "ARMV6",
        "ARMV5",

        # 8.ARM 64-bit CPU:
        "ARMV8",
        "CORTEXA53",
        "CORTEXA57",
        "CORTEXA72",
        "CORTEXA73",
        "CORTEXA510",
        "CORTEXA710",
        "CORTEXX1",
        "CORTEXX2",
        "NEOVERSEN1",
        "NEOVERSEV1",
        "NEOVERSEN2",
        "CORTEXA55",
        "EMAG8180",
        "FALKOR",
        "THUNDERX",
        "THUNDERX2T99",
        "TSV110",
        "THUNDERX3T110",
        "VORTEX",
        "A64FX",
        "ARMV8SVE",
        "FT2000",

        # 9.System Z:
        "ZARCH_GENERIC",
        "Z13",
        "Z14",

        # 10.RISC-V 64:
        "RISCV64_GENERIC",
        "C910V",

        # 11.LOONGARCH64:
        "LOONGSONGENERIC",
        "LOONGSON3R5",
        "LOONGSON2K1000",

        # 12. Elbrus E2000:
        "E2K",

        # 13. Alpha
        "EV4",
        "EV5",
        "EV6",
    ]

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
        "target": openblas_target_list,
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_lapack": False,
        "use_thread": True,
        "dynamic_arch": False,
        "target": "native",
    }
    generators = "cmake"
    short_paths = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if hasattr(self, "settings_build") and build.cross_building(self, skip_x64_x86=True):
            raise ConanInvalidConfiguration("Cross-building not implemented")

    def source(self):
        get(
            **self.conan_data["sources"][self.version],
            strip_root=True,
            destination=self._source_subfolder
        )

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)

        if self.options.build_lapack:
            self.output.warn("Building with lapack support requires a Fortran compiler.")
        cmake.definitions["NOFORTRAN"] = not self.options.build_lapack
        cmake.definitions["BUILD_WITHOUT_LAPACK"] = not self.options.build_lapack
        cmake.definitions["DYNAMIC_ARCH"] = self.options.dynamic_arch
        cmake.definitions["USE_THREAD"] = self.options.use_thread

        if self.options.target != "native":
            cmake.definitions["TARGET"] = self.options.target
            self.output.info(
                    f"Setting target arch to {self.options.target} and "
                    "passing this as value to TARGET variable of openblas cmake. "
                    "For more information, check out "
                    "https://github.com/xianyi/OpenBLAS#normal-compile")

        # Required for safe concurrent calls to OpenBLAS routines
        cmake.definitions["USE_LOCKING"] = not self.options.use_thread

        cmake.definitions[
            "MSVC_STATIC_CRT"
        ] = False  # don't, may lie to consumer, /MD or /MT is managed by conan

        # This is a workaround to add the libm dependency on linux,
        # which is required to successfully compile on older gcc versions.
        cmake.definitions["ANDROID"] = self.settings.os in ["Linux", "Android"]

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

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

        replace_in_file(
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
        rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(os.path.join(self.package_folder, "share"))

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
