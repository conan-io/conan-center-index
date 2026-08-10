from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, rm, export_conandata_patches, apply_conandata_patches
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
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
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        # INFO: matches Jolt's own CMake defaults (USE_SSE4_1/USE_SSE4_2/USE_AVX/USE_AVX2/USE_LZCNT/USE_TZCNT/
        # USE_F16C/USE_FMADD all ON, USE_AVX512 OFF)
        "simd": "avx2",
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch not in ("x86", "x86_64"):
            del self.options.simd

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.20 <4]")

    def validate(self):
        check_min_cppstd(self, 17)

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
        tc.cache_variables["CROSS_PLATFORM_DETERMINISTIC"] = False
        tc.cache_variables["INTERPROCEDURAL_OPTIMIZATION"] = False
        tc.cache_variables["GENERATE_DEBUG_SYMBOLS"] = False
        tc.cache_variables["ENABLE_ALL_WARNINGS"] = False
        tc.cache_variables["OVERRIDE_CXX_FLAGS"] = False
        tc.cache_variables["DEBUG_RENDERER_IN_DEBUG_AND_RELEASE"] = False
        tc.cache_variables["PROFILER_IN_DEBUG_AND_RELEASE"] = False
        # Disable GPU compute backends introduced in 5.6.0 (require optional SDKs)
        tc.cache_variables["JPH_USE_DX12"] = False
        tc.cache_variables["JPH_USE_VK"] = False
        tc.cache_variables["JPH_USE_MTL"] = False
        tc.cache_variables["JPH_USE_CPU_COMPUTE"] = False
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
            tc.cache_variables["USE_FMADD"]  = self._has_avx2
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
                                    ("JPH_USE_FMADD", self._has_avx2)):
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
                                              "-mavx2", "-mbmi", "-mpopcnt", "-mlzcnt",
                                              "-mf16c", "-mfma"])
                elif self._has_avx2:
                    tc.extra_cxxflags.extend(["-mavx2", "-mbmi", "-mpopcnt",
                                              "-mlzcnt", "-mf16c", "-mfma"])
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
        # INFO: The CMake option ENABLE_OBJECT_STREAM is enabled by default and defines JPH_OBJECT_STREAM as public
        # https://github.com/jrouwe/JoltPhysics/blob/v5.2.0/Build/CMakeLists.txt#L95C8-L95C28
        self.cpp_info.defines = ["JPH_OBJECT_STREAM"]
        # INFO: Public defines exposed in include/Jolt/Jolt.cmake
        # https://github.com/jrouwe/JoltPhysics/blob/v5.2.0/Build/CMakeLists.txt#L51
        if self.settings.arch in ("x86", "x86_64"):
            if self._has_sse41:
                self.cpp_info.defines.append("JPH_USE_SSE4_1")
            if self._has_sse42:
                self.cpp_info.defines.append("JPH_USE_SSE4_2")
            if self._has_avx:
                self.cpp_info.defines.append("JPH_USE_AVX")
            if self._has_avx2:
                self.cpp_info.defines.extend(["JPH_USE_AVX2", "JPH_USE_LZCNT",
                                              "JPH_USE_TZCNT", "JPH_USE_F16C", "JPH_USE_FMADD"])
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
                                                   "-mavx2", "-mbmi", "-mpopcnt", "-mlzcnt",
                                                   "-mf16c", "-mfma"])
                elif self._has_avx2:
                    self.cpp_info.cxxflags.extend(["-mavx2", "-mbmi", "-mpopcnt",
                                                   "-mlzcnt", "-mf16c", "-mfma"])
                elif self._has_avx:
                    self.cpp_info.cxxflags.extend(["-mavx", "-mpopcnt"])
                elif self._has_sse42:
                    self.cpp_info.cxxflags.extend(["-msse4.2", "-mpopcnt"])
                elif self._has_sse41:
                    self.cpp_info.cxxflags.append("-msse4.1")
                elif self.settings.arch == "x86":
                    self.cpp_info.cxxflags.append("-msse2")
        if is_msvc(self):
            # INFO: Floating point exceptions are enabled by default
            # https://github.com/jrouwe/JoltPhysics/blob/v5.2.0/Build/CMakeLists.txt#L37
            # https://github.com/jrouwe/JoltPhysics/blob/v5.2.0/Jolt/Jolt.cmake#L529
            self.cpp_info.defines.append("JPH_FLOATING_POINT_EXCEPTIONS_ENABLED")

        if self.options.shared:
            # https://github.com/jrouwe/JoltPhysics/blob/v5.2.0/Jolt/Jolt.cmake#L495
            self.cpp_info.defines.append("JPH_SHARED_LIBRARY")

        # https://github.com/jrouwe/JoltPhysics/blob/v5.2.0/Build/CMakeLists.txt#L48
        # https://github.com/jrouwe/JoltPhysics/blob/v5.2.0/Jolt/Jolt.cmake#L554
        self.cpp_info.defines.append("JPH_OBJECT_LAYER_BITS=16")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
