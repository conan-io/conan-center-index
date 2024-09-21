from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


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
        "fPIC": [True, False],

        "use_asserts": [True, False],
        "double_precision": [True, False],
        "generate_debug_symbols": [True, False],
        "override_cxx_flags": [True, False],
        "cross_platform_deterministic": [True, False],
        "cross_compile_arm": [True, False],
        "build_shared_libs": [True, False],
        "interprocedural_optimization": [True, False],
        "floating_point_exceptions_enabled": [True, False],
        "cpp_exceptions_enabled": [True, False],
        "cpp_rtti_enabled": [True, False],

        "object_layer_bits": [16, 32],

        "use_sse4_1": [True, False],
        "use_sse4_2": [True, False],
        "use_avx": [True, False],
        "use_avx2": [True, False],
        "use_avx512": [True, False],
        "use_lzcnt": [True, False],
        "use_tzcnt": [True, False],
        "use_f16c": [True, False],
        "use_fmadd": [True, False],

        "use_wasm_simd": [True, False],
        "enable_all_warnings": [True, False],

        "track_broadphase_stats": [True, False],
        "track_narrowphase_stats": [True, False],

        "debug_renderer": [True, False],
        "debug_renderer_in_debug_and_release": [True, False],
        "debug_renderer_in_distribution": [True, False],

        "profiler": [True, False],
        "profiler_in_debug_and_release": [True, False],
        "profiler_in_distribution": [True, False],

        "disable_custom_allocator": [True, False],
        "use_std_vector": [True, False],
        "enable_object_stream": [True, False],
        "enable_install": [True, False],
        "profile": [True, False],
    }
    default_options = {
        "build_shared_libs": False,
        "fPIC": True,

        "use_asserts": False,
        "double_precision": False,
        "generate_debug_symbols": True,
        "override_cxx_flags": True,
        "cross_platform_deterministic": False,
        "cross_compile_arm": False,
        "build_shared_libs": False,
        "interprocedural_optimization": True,
        "floating_point_exceptions_enabled": False,
        "cpp_exceptions_enabled": False,
        "cpp_rtti_enabled": False,
        "object_layer_bits": 16,

        "use_sse4_1": True,
        "use_sse4_2": True,
        "use_avx": True,
        "use_avx2": True,
        "use_avx512": False,
        "use_lzcnt": True,
        "use_tzcnt": True,
        "use_f16c": True,
        "use_fmadd": True,

        "use_wasm_simd": False,
        "enable_all_warnings": True,

        "track_broadphase_stats": False,
        "track_narrowphase_stats": False,

        "debug_renderer": False, # so long as the following two options are false, this variable comes into effect, this is added as a custom conan option so that you can have custom debug renderer behavior
        "debug_renderer_in_debug_and_release": True,
        "debug_renderer_in_distribution": False,

        "profiler": False, # so long as the following two options are false, this variable comes into effect, this is added as a custom conan option so that you can have custom profiler behavior
        "profiler_in_debug_and_release": True,
        "profiler_in_distribution": False,

        "disable_custom_allocator": False,
        "use_std_vector": False,
        "enable_object_stream": True,
        "enable_install": True,
    }

    @property
    def _min_cppstd(self):
        return "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "9.2", # due to https://gcc.gnu.org/bugzilla/show_bug.cgi?id=81429
            "clang": "5",
            "apple-clang": "12",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        # if self.settings.arch not in ("x86", "x86_64"):
        #     del self.options.simd

    def configure(self):
        if self.options.build_shared_libs:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and loose_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

        if is_msvc(self) and self.options.build_shared_libs:
            raise ConanInvalidConfiguration(f"{self.ref} shared not supported with Visual Studio")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # Disable all testing: https://github.com/conan-io/conan-center-index/blob/master/docs/adding_packages/conanfile_attributes.md#options-to-avoid
        tc.variables["TARGET_UNIT_TESTS"] = False
        tc.variables["TARGET_HELLO_WORLD"] = False
        tc.variables["TARGET_PERFORMANCE_TEST"] = False
        tc.variables["TARGET_SAMPLES"] = False
        tc.variables["TARGET_VIEWER"] = False
        tc.variables["GENERATE_DEBUG_SYMBOLS"] = False
        tc.variables["TARGET_UNIT_TESTS"] = False

        if is_msvc(self):
            tc.variables["USE_STATIC_MSVC_RUNTIME_LIBRARY"] = is_msvc_static_runtime(self)

        tc.variables["USE_ASSERTS"] = self.options.use_asserts
        tc.variables["DOUBLE_PRECISION"] = self.options.double_precision
        tc.variables["GENERATE_DEBUG_SYMBOLS"] = self.options.generate_debug_symbols
        tc.variables["OVERRIDE_CXX_FLAGS"] = self.options.override_cxx_flags
        tc.variables["CROSS_PLATFORM_DETERMINISTIC"] = self.options.cross_platform_deterministic
        tc.variables["CROSS_COMPILE_ARM"] = self.options.cross_compile_arm
        tc.variables["BUILD_SHARED_LIBS"] = self.options.build_shared_libs
        tc.variables["INTERPROCEDURAL_OPTIMIZATION"] = self.options.interprocedural_optimization
        tc.variables["FLOATING_POINT_EXCEPTIONS_ENABLED"] = self.options.floating_point_exceptions_enabled
        tc.variables["CPP_EXCEPTIONS_ENABLED"] = self.options.cpp_exceptions_enabled
        tc.variables["CPP_RTTI_ENABLED"] = self.options.cpp_rtti_enabled
        tc.variables["OBJECT_LAYER_BITS"] = self.options.object_layer_bits

        # Select X86 processor features to use
        tc.variables["USE_SSE4_1"] = self.options.use_sse4_1
        tc.variables["USE_SSE4_2"] = self.options.use_sse4_2
        tc.variables["USE_AVX"] = self.options.use_avx
        tc.variables["USE_AVX2"] = self.options.use_avx2
        tc.variables["USE_AVX512"] = self.options.use_avx512
        tc.variables["USE_LZCNT"] = self.options.use_lzcnt
        tc.variables["USE_TZCNT"] = self.options.use_tzcnt
        tc.variables["USE_F16C"] = self.options.use_f16c
        tc.variables["USE_FMADD"] = self.options.use_fmadd

        tc.variables["USE_WASM_SIMD"] = self.options.use_wasm_simd
        tc.variables["ENABLE_ALL_WARNINGS"] = self.options.enable_all_warnings
        tc.variables["TRACK_BROADPHASE_STATS"] = self.options.track_broadphase_stats
        tc.variables["TRACK_NARROWPHASE_STATS"] = self.options.track_narrowphase_stats

        tc.variables["DEBUG_RENDERER_IN_DEBUG_AND_RELEASE"] = self.options.debug_renderer_in_debug_and_release
        tc.variables["DEBUG_RENDERER_IN_DISTRIBUTION"] = self.options.debug_renderer_in_distribution

        tc.variables["PROFILER_IN_DEBUG_AND_RELEASE"] = self.options.profiler_in_debug_and_release
        tc.variables["PROFILER_IN_DISTRIBUTION"] = self.options.profiler_in_distribution

        tc.variables["DISABLE_CUSTOM_ALLOCATOR"] = self.options.disable_custom_allocator
        tc.variables["USE_STD_VECTOR"] = self.options.use_std_vector
        tc.variables["ENABLE_OBJECT_STREAM"] = self.options.enable_object_stream
        tc.variables["ENABLE_INSTALL"] = self.options.enable_install


        # if Version(self.version) >= "3.0.0":
        #     tc.variables["ENABLE_ALL_WARNINGS"] = False
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "Build"))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["Jolt"]

        # if both options are false
        if (not self.options.profiler_in_debug_and_release and not self.options.profiler_in_distribution):
            # but you want custom behavior
            if (self.options.profiler):
                self.cpp_info.defines.append("JPH_PROFILE_ENABLED")

        if (not self.options.debug_renderer_in_debug_and_release and not self.options.debug_renderer_in_distribution):
            if (self.options.debug_renderer):
                self.cpp_info.defines.append("JPH_DEBUG_RENDERER")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
