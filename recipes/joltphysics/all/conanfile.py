from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
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
        "shared": [True, False],
        "fPIC": [True, False],
        "simd": ["sse", "sse41", "sse42", "avx", "avx2", "avx512"],
        "debug_renderer": [True, False],
        "profile": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "simd": "sse42",
        "debug_renderer": False,
        "profile": False,
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

    @property
    def _has_sse41(self):
        return self.options.get_safe("simd") in ("sse41", "sse42", "avx", "avx2", "avx512")

    @property
    def _has_sse42(self):
        return self.options.get_safe("simd") in ("sse42", "avx", "avx2", "avx512")

    @property
    def _has_avx(self):
        return self.options.get_safe("simd") in ("avx", "avx2", "avx512")

    @property
    def _has_avx2(self):
        return self.options.get_safe("simd") in ("avx2", "avx512")

    @property
    def _has_avx512(self):
        return self.options.get_safe("simd") == "avx512"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch not in ("x86", "x86_64"):
            del self.options.simd

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

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

        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} shared not supported with Visual Studio")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["TARGET_UNIT_TESTS"] = False
        tc.variables["TARGET_HELLO_WORLD"] = False
        tc.variables["TARGET_PERFORMANCE_TEST"] = False
        tc.variables["TARGET_SAMPLES"] = False
        tc.variables["TARGET_VIEWER"] = False
        tc.variables["GENERATE_DEBUG_SYMBOLS"] = False
        tc.variables["TARGET_UNIT_TESTS"] = False
        tc.variables["USE_SSE4_1"] = self._has_sse41
        tc.variables["USE_SSE4_2"] = self._has_sse42
        tc.variables["USE_AVX"] = self._has_avx
        tc.variables["USE_AVX2"] = self._has_avx2
        tc.variables["USE_AVX512"] = self._has_avx512
        if is_msvc(self):
            tc.variables["USE_STATIC_MSVC_RUNTIME_LIBRARY"] = is_msvc_static_runtime(self)
        tc.variables["JPH_DEBUG_RENDERER"] = self.options.debug_renderer
        tc.variables["JPH_PROFILE_ENABLED"] = self.options.profile
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
        if self._has_sse41:
            self.cpp_info.defines.append("JPH_USE_SSE4_1")
        if self._has_sse42:
            self.cpp_info.defines.append("JPH_USE_SSE4_2")
        if self._has_avx:
            self.cpp_info.defines.append("JPH_USE_AVX")
        if self._has_avx2:
            self.cpp_info.defines.append("JPH_USE_AVX2")
        if self._has_avx512:
            self.cpp_info.defines.append("JPH_USE_AVX512")
        if self.options.debug_renderer:
            self.cpp_info.defines.append("JPH_DEBUG_RENDERER")
        if self.options.profile:
            self.cpp_info.defines.append("JPH_PROFILE_ENABLED")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
