from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir, export_conandata_patches, apply_conandata_patches
from conan.tools.microsoft import is_msvc_static_runtime, is_msvc
import os

required_conan_version = ">=1.53.0"

# Maps Conan's settings.arch to the corresponding OpenBLAS TARGET:
conan_arch_to_openblas_target = {
    "x86": "SANDYBRIDGE",  # Sandy bridge was discontinued in September of 2013,
    "x86_64": "SANDYBRIDGE",  # supporting older CPUs is a performance trade-off
    "ppc32be": None,  # TODO: OpenBLAS has POWER4, POWER5, POWER6, POWER7,
    "ppc32": None,  #         POWER8, POWER9, POWER10, PPCG4, PPC970, PPC970MP,
    "ppc64le": None,  #       PPC440, PPC440FP2, CELL
    "ppc64": None,
    "armv4": None,  # Not supported by OpenBLAS
    "armv4i": None,  # Not supported by OpenBLAS
    "armv5el": "ARMV5",
    "armv5hf": "ARMV5",
    "armv6": "ARMV6",
    "armv7": "ARMV7",
    "armv7hf": "ARMV7",
    "armv7s": "ARMV7",
    "armv7k": "ARMV7",
    "armv8": "ARMV8",
    "armv8_32": "ARMV7",  # No 32-bit ARMv8 TARGET in OpenBLAS
    "armv8.3": "ARMV8",
    "arm64ec": "ARMV8",
    "sparc": None,  # TODO: OpenBLAS has SPARC, SPARCV7
    "sparcv9": None,
    "mips": None,  # TODO: OpenBLAS has P5600, MIPS1004K and MIPS24K
    "mips64": "MIPS64_GENERIC",
    "avr": None,  # Not supported by OpenBLAS
    "s390": None,  # Not supported by OpenBLAS
    "s390x": None,  # Not supported by OpenBLAS
    "asm.js": "GENERIC",  # TODO: ?
    "wasm": "GENERIC",  # TODO: ?
    "sh4le": None,  # Not supported by OpenBLAS
    "e2k-v2": "E2K",
    "e2k-v3": "E2K",
    "e2k-v4": "E2K",
    "e2k-v5": "E2K",
    "e2k-v6": "E2K",
    "e2k-v7": "E2K",
    "riscv64": "RISCV64_GENERIC",
    "riscv32": None,  # Not supported by OpenBLAS
    "xtensalx6": None,  # Not supported by OpenBLAS
    "xtensalx106": None,  # Not supported by OpenBLAS
    "xtensalx7": None,  # Not supported by OpenBLAS
}

# Taken from OpenBLAS TargetList.txt
available_openblas_targets = ["P2", "KATMAI", "COPPERMINE", "NORTHWOOD", "PRESCOTT", "BANIAS", "YONAH", "CORE2", "PENRYN", "DUNNINGTON", "NEHALEM", "SANDYBRIDGE", "HASWELL", "SKYLAKEX", "ATOM", "COOPERLAKE", "SAPPHIRERAPIDS", "ATHLON", "OPTERON", "OPTERON_SSE3", "BARCELONA", "SHANGHAI", "ISTANBUL", "BOBCAT", "BULLDOZER", "PILEDRIVER", "STEAMROLLER", "EXCAVATOR", "ZEN", "SSE_GENERIC", "VIAC3", "NANO", "POWER4", "POWER5", "POWER6", "POWER7", "POWER8", "POWER9", "POWER10", "PPCG4", "PPC970", "PPC970MP", "PPC440", "PPC440FP2", "CELL", "P5600", "MIPS1004K", "MIPS24K", "MIPS64_GENERIC", "SICORTEX", "LOONGSON3A", "LOONGSON3B", "I6400", "P6600", "I6500", "ITANIUM2", "SPARC", "SPARCV7", "CORTEXA15", "CORTEXA9", "ARMV7", "ARMV6", "ARMV5", "ARMV8", "CORTEXA53", "CORTEXA57", "CORTEXA72", "CORTEXA73", "CORTEXA76", "CORTEXA510", "CORTEXA710", "CORTEXX1", "CORTEXX2", "NEOVERSEN1", "NEOVERSEV1", "NEOVERSEN2", "CORTEXA55", "EMAG8180", "FALKOR", "THUNDERX", "THUNDERX2T99", "TSV110", "THUNDERX3T110", "VORTEX", "A64FX", "ARMV8SVE", "FT2000", "ZARCH_GENERIC", "Z13", "Z14", "RISCV64_GENERIC", "RISCV64_ZVL128B", "C910V", "x280", "RISCV64_ZVL256B", "LOONGSONGENERIC", "LOONGSON3R5", "LOONGSON2K1000", "E2K", "EV4", "EV5", "EV6", "CSKY", "CK860FV"]


class OpenblasConan(ConanFile):
    name = "openblas"
    description = "An optimized BLAS library based on GotoBLAS2, with LAPACK"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.openblas.net"
    topics = ("blas", "lapack")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "ilp64": [True, False],
        "build_lapack": [True, False],
        "build_relapack": [True, False],
        "build_bfloat16": [True, False],
        "use_openmp": [True, False],
        "use_thread": [True, False],
        "use_locking": [True, False],
        "dynamic_arch": [True, False],
        "target": [None] + available_openblas_targets,
        "max_threads": ["auto", "ANY"],
        "max_omp_parallel": ["ANY"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "ilp64": False,
        "build_lapack": True,
        "build_relapack": False,
        "build_bfloat16": False,
        "use_openmp": True,
        "use_thread": True,
        "use_locking": True,
        "dynamic_arch": False,
        "target": None,
        "max_threads": 128,
        "max_omp_parallel": 1,
    }
    options_description = {
        "ilp64": "Build with ILP64 interface instead of LP64 (incompatible with the standard API)",
        "build_lapack": "Build LAPACK and LAPACKE",
        "build_relapack": "Build with ReLAPACK (recursive implementation of several LAPACK functions on top of standard LAPACK)",
        "build_bfloat16": "Build with bfloat16 support",
        "use_openmp": "Enable OpenMP support",
        "use_thread": "Enable threads support",
        "use_locking": "Use locks even in single-threaded builds to make them callable from multiple threads",
        "dynamic_arch": "Include support for multiple CPU targets, with automatic selection at runtime (x86/x86_64, aarch64 or ppc only)",
        "target": "OpenBLAS TARGET variable (see TargetList.txt)",
        "max_threads": "The maximum number of parallel threads you expect to need (defaults to the number of cores in the build cpu)",
        "max_omp_parallel": "Number of OpenMP instances that your code may use for parallel calls into OpenBLAS",
    }
    options_description = {
        "ilp64": "Build with ILP64 interface instead of LP64 (incompatible with the standard API)",
        "build_lapack": "Build LAPACK and LAPACKE",
        "build_relapack": "Build with ReLAPACK (recursive implementation of several LAPACK functions on top of standard LAPACK)",
        "build_bfloat16": "Build with bfloat16 support",
        "use_openmp": "Enable OpenMP support",
        "use_thread": "Enable threads support",
        "use_locking": "Use locks even in single-threaded builds to make them callable from multiple threads",
        "dynamic_arch": "Include support for multiple CPU targets, with automatic selection at runtime (x86/x86_64, aarch64 or ppc only)",
    }
    short_paths = True

    @property
    def _fortran_compiler(self):
        comp_exe = self.conf.get("tools.build:compiler_executables")
        if comp_exe and "fortran" in comp_exe:
            return comp_exe["fortran"]
        return None

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.build_lapack:
            del self.options.build_relapack
        if not self.options.use_thread:
            del self.options.max_threads
        if not self.options.use_openmp:
            del self.options.max_omp_parallel

        # When cross-compiling, OpenBLAS requires explicitly setting TARGET
        if cross_building(self, skip_x64_x86=True) and not self.options.target:
            # Try inferring the target from settings.arch
            target = conan_arch_to_openblas_target.get(str(self.settings.arch))
            if target:
                self.output.warning(
                    f"Setting OpenBLAS TARGET={target} based on settings.arch. "
                    "This may result in suboptimal performance. "
                    f'Set the "{self.name}/*:target=XXX" option to silence this warning.'
                )
                self.options.target = target

    def requirements(self):
        if self.options.use_openmp and self.settings.compiler in ["clang", "apple-clang"]:
            self.requires("llvm-openmp/17.0.6")

    def validate(self):
        if self.options.get_safe("build_relapack") and self.settings.compiler not in ["gcc", "clang"]:
            # ld: unknown option: --allow-multiple-definition on apple-clang
            raise ConanInvalidConfiguration(f'"{self.name}/*:build_relapack=True" option is only supported for GCC and Clang')

    def build_requirements(self):
        if self.options.use_openmp:
            self.tool_requires("cmake/[>=3.16 <4]")

    def validate_build(self):
        # If we're cross-compiling, and the user didn't provide the target, and
        # we couldn't infer the target from settings.arch, fail
        if cross_building(self, skip_x64_x86=True) and not self.options.target:
            raise ConanInvalidConfiguration(f'Could not determine OpenBLAS TARGET. Please set the "{self.name}/*:target=XXX" option.')

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        VirtualBuildEnv(self).generate()

        tc = CMakeToolchain(self)
        tc.variables["BUILD_STATIC_LIBS"] = not self.options.shared
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["BUILD_TESTING"] = False

        tc.variables["NOFORTRAN"] = not self.options.build_lapack
        if self.options.build_lapack and not self._fortran_compiler:
            tc.variables["C_LAPACK"] = True
            tc.variables["NOFORTRAN"] = True
            self.output.info("Building LAPACK without a Fortran compiler")

        tc.variables["BUILD_WITHOUT_LAPACK"] = not self.options.build_lapack
        tc.variables["BUILD_RELAPACK"] = self.options.get_safe("build_relapack", False)
        tc.variables["BUILD_BFLOAT16"] = self.options.build_bfloat16
        tc.variables["INTERFACE64"] = self.options.ilp64
        tc.variables["DYNAMIC_ARCH"] = self.options.dynamic_arch
        tc.variables["USE_OPENMP"] = self.options.use_openmp
        tc.variables["USE_THREAD"] = self.options.use_thread
        tc.variables["USE_LOCKING"] = self.options.use_locking
        if self.options.get_safe("max_threads", "auto") != "auto":
            tc.variables["NUM_PARALLEL"] = self.options.max_threads
        if self.options.get_safe("max_omp_parallel"):
            tc.variables["NUM_THREADS"] = self.options.max_omp_parallel

        tc.variables["MSVC_STATIC_CRT"] = is_msvc_static_runtime(self)

        # Needed for $<$<LINK_LANGUAGE:C>:OpenMP::OpenMP_C> to work correctly
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0022"] = "NEW"

        # This is a workaround to add the libm dependency on linux,
        # which is required to successfully compile on older gcc versions.
        tc.variables["ANDROID"] = self.settings.os in ["Linux", "Android"]

        if self.options.target:
            tc.cache_variables["TARGET"] = self.options.target

        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)

    @property
    def _lib_name(self):
        name = "openblas"
        if self.options.ilp64:
            name += "_64"
        if self.options.shared and self.settings.build_type == "Debug" and not is_msvc(self):
            name += "_d"
        return name

    @property
    def _64bit(self):
        return "64" if self.options.ilp64 else ""

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", f"OpenBLAS{self._64bit}")
        self.cpp_info.set_property("cmake_target_name", "OpenBLAS::OpenBLAS")
        if self.options.ilp64:
            self.cpp_info.set_property("cmake_target_aliases", ["OpenBLAS64::OpenBLAS"])
        self.cpp_info.set_property("pkg_config_name", f"openblas{self._64bit}")
        self.cpp_info.components["openblas_component"].set_property("pkg_config_name", f"openblas{self._64bit}")
        self.cpp_info.components["openblas_component"].includedirs.append(os.path.join("include", f"openblas{self._64bit}"))
        self.cpp_info.components["openblas_component"].libs = [self._lib_name]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["openblas_component"].system_libs.append("m")
            if self.options.use_thread:
                self.cpp_info.components["openblas_component"].system_libs.append("pthread")
            if self.options.build_lapack and self._fortran_compiler:
                self.cpp_info.components["openblas_component"].system_libs.append("gfortran")

        if self.options.use_openmp:
            if self.options.use_openmp and self.settings.compiler in ["clang", "apple-clang"]:
                self.cpp_info.components["openblas_component"].requires.append("llvm-openmp::llvm-openmp")
            else:
                if is_msvc(self):
                    openmp_flags = ["-openmp"]
                elif self.settings.compiler == "gcc":
                    openmp_flags = ["-fopenmp"]
                elif self.settings.compiler == "intel-cc":
                    openmp_flags = ["-Qopenmp"]
                self.cpp_info.exelinkflags.extend(openmp_flags)
                self.cpp_info.sharedlinkflags.extend(openmp_flags)

        # OpenBLAS always has one and only one of these components defined: openmp, pthread or serial.
        if self.options.use_openmp:
            component = "openmp"
        elif self.options.use_thread:
            component = "pthread"
        else:
            component = "serial"
        self.cpp_info.components[component].set_property("cmake_target_name", f"OpenBLAS::{component}")
        self.cpp_info.components[component].requires = ["openblas_component"]

        self.buildenv_info.define_path("OpenBLAS_HOME", self.package_folder)
        self.runenv_info.define_path("OpenBLAS_HOME", self.package_folder)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = f"OpenBLAS{self._64bit}"
        self.cpp_info.filenames["cmake_find_package_multi"] = f"OpenBLAS{self._64bit}"
        self.cpp_info.names["cmake_find_package"] = "OpenBLAS"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenBLAS"
        self.env_info.OpenBLAS_HOME = self.package_folder
