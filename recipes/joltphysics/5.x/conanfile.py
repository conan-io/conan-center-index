from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, rm, export_conandata_patches, apply_conandata_patches
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=2.0.9"


class JoltPhysicsConan(ConanFile):
    name = "joltphysics"
    description = (
        "A multi core friendly rigid body physics and collision detection "
        "library, written in C++, suitable for games and VR applications."
    )
    license = "MIT"
    topics = ("physics", "simulation", "physics-engine", "physics-simulation", "rigid-body", "game", "collision")
    homepage = "https://github.com/jrouwe/JoltPhysics"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        # INFO: sse2 is the x86 baseline, Jolt has no CMake option for it: Core.h defines JPH_USE_SSE for every x86
        # target and each higher level is opt-in. It is a named value rather than None because Conan does not let a
        # consumer select None, that value is only reachable as a recipe default.
        "simd": ["sse2", "sse41", "sse42", "avx", "avx2", "avx512"],
        "double_precision": [True, False],
        "object_layer_bits": [16, 32],
        "cross_platform_deterministic": [True, False],
        "object_stream": [True, False],
        "enable_asserts": [True, False],
        "custom_allocator": [True, False],
        "use_std_vector": [True, False],
        "cpu_compute": [True, False],
        "floating_point_exceptions": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        # INFO: matches Jolt's own CMake defaults (USE_SSE4_1/USE_SSE4_2/USE_AVX/USE_AVX2/USE_LZCNT/USE_TZCNT/
        # USE_F16C/USE_FMADD all ON, USE_AVX512 OFF)
        "simd": "avx2",
        "double_precision": False,
        "object_layer_bits": 16,
        "cross_platform_deterministic": False,
        "object_stream": True,
        "enable_asserts": False,
        "custom_allocator": True,
        "use_std_vector": False,
        "cpu_compute": False,
        # INFO: matches Jolt's own FLOATING_POINT_EXCEPTIONS_ENABLED default
        "floating_point_exceptions": True,
    }
    implements = ["auto_shared_fpic"]

    @property
    def _has_sse41(self):
        return str(self.options.get_safe("simd")) in ("sse41", "sse42", "avx", "avx2", "avx512")

    @property
    def _has_sse42(self):
        return str(self.options.get_safe("simd")) in ("sse42", "avx", "avx2", "avx512")

    @property
    def _has_avx(self):
        return str(self.options.get_safe("simd")) in ("avx", "avx2", "avx512")

    @property
    def _has_avx2(self):
        return str(self.options.get_safe("simd")) in ("avx2", "avx512")

    @property
    def _has_avx512(self):
        return str(self.options.get_safe("simd")) == "avx512"

    @property
    def _has_fmadd(self):
        return self._has_avx2 and not self.options.cross_platform_deterministic

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch not in ("x86", "x86_64"):
            del self.options.simd
        # INFO: Jolt only ever defines JPH_FLOATING_POINT_EXCEPTIONS_ENABLED for MSVC
        if not is_msvc(self):
            del self.options.floating_point_exceptions

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.20 <4]")

    def validate(self):
        check_min_cppstd(self, 17)
        if self.options.get_safe("cpu_compute") and Version(self.version) < "5.6.0":
            raise ConanInvalidConfiguration(f"{self.ref} does not support cpu_compute, requires >= 5.6.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["TARGET_UNIT_TESTS"] = False
        tc.cache_variables["TARGET_HELLO_WORLD"] = False
        tc.cache_variables["TARGET_PERFORMANCE_TEST"] = False
        tc.cache_variables["TARGET_SAMPLES"] = False
        tc.cache_variables["TARGET_VIEWER"] = False
        tc.cache_variables["INTERPROCEDURAL_OPTIMIZATION"] = False
        tc.cache_variables["GENERATE_DEBUG_SYMBOLS"] = False
        tc.cache_variables["ENABLE_ALL_WARNINGS"] = False
        tc.cache_variables["OVERRIDE_CXX_FLAGS"] = False
        tc.cache_variables["DEBUG_RENDERER_IN_DEBUG_AND_RELEASE"] = False
        tc.cache_variables["PROFILER_IN_DEBUG_AND_RELEASE"] = False
        # Disable GPU compute backends (require optional SDKs: DX12, Vulkan, Metal)
        tc.cache_variables["JPH_USE_DX12"] = False
        tc.cache_variables["JPH_USE_VK"] = False
        tc.cache_variables["JPH_USE_MTL"] = False
        tc.cache_variables["CROSS_PLATFORM_DETERMINISTIC"] = bool(self.options.cross_platform_deterministic)
        tc.cache_variables["DOUBLE_PRECISION"] = bool(self.options.double_precision)
        tc.cache_variables["OBJECT_LAYER_BITS"] = int(str(self.options.object_layer_bits))
        tc.cache_variables["ENABLE_OBJECT_STREAM"] = bool(self.options.object_stream)
        tc.cache_variables["USE_ASSERTS"] = bool(self.options.enable_asserts)
        tc.cache_variables["DISABLE_CUSTOM_ALLOCATOR"] = not bool(self.options.custom_allocator)
        tc.cache_variables["USE_STD_VECTOR"] = bool(self.options.use_std_vector)
        tc.cache_variables["JPH_USE_CPU_COMPUTE"] = bool(self.options.cpu_compute)
        tc.cache_variables["FLOATING_POINT_EXCEPTIONS_ENABLED"] = bool(
            self.options.get_safe("floating_point_exceptions", False))
        if is_msvc(self):
            tc.cache_variables["USE_STATIC_MSVC_RUNTIME_LIBRARY"] = is_msvc_static_runtime(self)
        if self.settings.arch in ("x86", "x86_64"):
            tc.cache_variables["USE_SSE4_1"] = self._has_sse41
            tc.cache_variables["USE_SSE4_2"] = self._has_sse42
            tc.cache_variables["USE_AVX"]    = self._has_avx
            tc.cache_variables["USE_AVX2"]   = self._has_avx2
            tc.cache_variables["USE_AVX512"] = self._has_avx512
            tc.cache_variables["USE_LZCNT"]  = self._has_avx2
            tc.cache_variables["USE_TZCNT"]  = self._has_avx2
            tc.cache_variables["USE_F16C"]   = self._has_avx2
            tc.cache_variables["USE_FMADD"]  = self._has_fmadd
            # INFO: Jolt emits the JPH_USE_* defines from EMIT_X86_INSTRUCTION_SET_DEFINITIONS(), which its CMake
            # calls only inside a branch guarded on CMAKE_VS_PLATFORM_NAME being x86 or x64. That variable is empty
            # for every generator other than Visual Studio, so under Ninja the library is compiled without them
            # while package_info() still exports them to consumers. They are public and change the layout of DVec3
            # (__m256d under JPH_USE_AVX, three doubles without), and unlike Jolt's other configuration defines they
            # are not part of JPH_VERSION_ID, so RegisterTypes() cannot catch the mismatch and it corrupts silently.
            # Set them here so they follow the selected option rather than the generator.
            # https://github.com/jrouwe/JoltPhysics/blob/v5.6.0/Jolt/Jolt.cmake#L969-L979
            for define, enabled in (("JPH_USE_SSE4_1", self._has_sse41),
                                    ("JPH_USE_SSE4_2", self._has_sse42),
                                    ("JPH_USE_AVX", self._has_avx),
                                    ("JPH_USE_AVX2", self._has_avx2),
                                    ("JPH_USE_AVX512", self._has_avx512),
                                    ("JPH_USE_LZCNT", self._has_avx2),
                                    ("JPH_USE_TZCNT", self._has_avx2),
                                    ("JPH_USE_F16C", self._has_avx2),
                                    ("JPH_USE_FMADD", self._has_fmadd)):
                if enabled:
                    tc.preprocessor_definitions[define] = None
            # Inject the ISA flags explicitly for the same reason: under Ninja the block above is skipped, so this
            # is the only source of them. Harmlessly duplicated under the Visual Studio generator.
            if is_msvc(self):
                if self._has_avx512:
                    tc.extra_cxxflags.append("/arch:AVX512")
                elif self._has_avx2:
                    tc.extra_cxxflags.append("/arch:AVX2")
                elif self._has_avx:
                    tc.extra_cxxflags.append("/arch:AVX")
            else:
                if self._has_avx512:
                    tc.extra_cxxflags.extend(["-mavx512f", "-mavx512vl", "-mavx512dq",
                                              "-mavx2", "-mbmi", "-mpopcnt", "-mlzcnt", "-mf16c"])
                    if self._has_fmadd:
                        tc.extra_cxxflags.append("-mfma")
                elif self._has_avx2:
                    tc.extra_cxxflags.extend(["-mavx2", "-mbmi", "-mpopcnt", "-mlzcnt", "-mf16c"])
                    if self._has_fmadd:
                        tc.extra_cxxflags.append("-mfma")
                elif self._has_avx:
                    tc.extra_cxxflags.extend(["-mavx", "-mpopcnt"])
                elif self._has_sse42:
                    tc.extra_cxxflags.extend(["-msse4.2", "-mpopcnt"])
                elif self._has_sse41:
                    tc.extra_cxxflags.append("-msse4.1")
                elif self.settings.arch == "x86":
                    # INFO: Jolt defines JPH_USE_SSE for every x86 target, which the 32 bit ABI does not guarantee.
                    # 64 bit needs no flag, SSE2 is part of that ABI, and MSVC already defaults to /arch:SSE2 on x86.
                    tc.extra_cxxflags.append("-msse2")
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "Build"))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.cmake", os.path.join(self.package_folder, "include", "Jolt"))

    def package_info(self):
        self.cpp_info.libs = ["Jolt"]
        self.cpp_info.set_property("cmake_file_name", "Jolt")
        self.cpp_info.set_property("cmake_target_name", "Jolt::Jolt")

        if self.options.object_stream:
            self.cpp_info.defines.append("JPH_OBJECT_STREAM")
        if self.options.double_precision:
            self.cpp_info.defines.append("JPH_DOUBLE_PRECISION")
        if self.options.cross_platform_deterministic:
            self.cpp_info.defines.append("JPH_CROSS_PLATFORM_DETERMINISTIC")
        if self.options.enable_asserts:
            self.cpp_info.defines.append("JPH_ENABLE_ASSERTS")
        if not self.options.custom_allocator:
            self.cpp_info.defines.append("JPH_DISABLE_CUSTOM_ALLOCATOR")
        if self.options.use_std_vector:
            self.cpp_info.defines.append("JPH_USE_STD_VECTOR")
        if self.options.cpu_compute:
            self.cpp_info.defines.append("JPH_USE_CPU_COMPUTE")

        # INFO: Public defines and compiler flags for x86 ISA extensions
        # https://github.com/jrouwe/JoltPhysics/blob/v5.6.0/Jolt/Jolt.cmake
        if self.settings.arch in ("x86", "x86_64"):
            if self._has_sse41:
                self.cpp_info.defines.append("JPH_USE_SSE4_1")
            if self._has_sse42:
                self.cpp_info.defines.append("JPH_USE_SSE4_2")
            if self._has_avx:
                self.cpp_info.defines.append("JPH_USE_AVX")
            if self._has_avx2:
                self.cpp_info.defines.extend(["JPH_USE_AVX2", "JPH_USE_LZCNT",
                                              "JPH_USE_TZCNT", "JPH_USE_F16C"])
            if self._has_fmadd:
                self.cpp_info.defines.append("JPH_USE_FMADD")
            if self._has_avx512:
                self.cpp_info.defines.append("JPH_USE_AVX512")
            # Propagate ISA flags so consumer TUs compiling Jolt's SIMD-guarded headers
            # have the matching instruction set enabled
            if is_msvc(self):
                if self._has_avx512:
                    self.cpp_info.cxxflags.append("/arch:AVX512")
                elif self._has_avx2:
                    self.cpp_info.cxxflags.append("/arch:AVX2")
                elif self._has_avx:
                    self.cpp_info.cxxflags.append("/arch:AVX")
            else:
                if self._has_avx512:
                    self.cpp_info.cxxflags.extend(["-mavx512f", "-mavx512vl", "-mavx512dq",
                                                   "-mavx2", "-mbmi", "-mpopcnt", "-mlzcnt", "-mf16c"])
                    if self._has_fmadd:
                        self.cpp_info.cxxflags.append("-mfma")
                elif self._has_avx2:
                    self.cpp_info.cxxflags.extend(["-mavx2", "-mbmi", "-mpopcnt", "-mlzcnt", "-mf16c"])
                    if self._has_fmadd:
                        self.cpp_info.cxxflags.append("-mfma")
                elif self._has_avx:
                    self.cpp_info.cxxflags.extend(["-mavx", "-mpopcnt"])
                elif self._has_sse42:
                    self.cpp_info.cxxflags.extend(["-msse4.2", "-mpopcnt"])
                elif self._has_sse41:
                    self.cpp_info.cxxflags.append("-msse4.1")
                elif self.settings.arch == "x86":
                    self.cpp_info.cxxflags.append("-msse2")

        # INFO: Jolt applies this define only to the Debug and Release configurations, so a package built as
        # RelWithDebInfo has it compiled out even when the option is enabled. It is one of the JPH_VERSION_ID
        # feature bits and RegisterTypesInternal() calls std::abort() on a mismatch, so what is exported here
        # has to track the configuration that was actually compiled, not just the option.
        # https://github.com/jrouwe/JoltPhysics/blob/v5.6.0/Jolt/Jolt.cmake#L840
        if (is_msvc(self) and bool(self.options.get_safe("floating_point_exceptions"))
                and str(self.settings.build_type) in ("Debug", "Release")):
            self.cpp_info.defines.append("JPH_FLOATING_POINT_EXCEPTIONS_ENABLED")

        if self.options.shared:
            self.cpp_info.defines.append("JPH_SHARED_LIBRARY")

        self.cpp_info.defines.append(f"JPH_OBJECT_LAYER_BITS={self.options.object_layer_bits}")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
