import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, apply_conandata_patches, export_conandata_patches
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class WhisperCppConan(ConanFile):
    name = "whisper-cpp"
    description = "High-performance inference of OpenAI's Whisper automatic speech recognition (ASR) model"
    topics = ("whisper", "asr")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ggerganov/whisper.cpp"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "sanitize_thread": [True, False],
        "sanitize_address": [True, False],
        "sanitize_undefined": [True, False],
        "no_avx": [True, False],
        "no_avx2": [True, False],
        "no_fma": [True, False],
        "no_f16c": [True, False],
        "no_accelerate": [True, False],
        "metal": [True, False],
        "metal_ndebug": [True, False],
        "with_coreml": [True, False],
        "coreml_allow_fallback": [True, False],
        "with_blas": [True, False],
        "with_openvino": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "sanitize_thread": False,
        "sanitize_address": False,
        "sanitize_undefined": False,
        "no_avx": False,
        "no_avx2": False,
        "no_fma": False,
        "no_f16c": False,
        "no_accelerate": False,
        "metal": False,
        "metal_ndebug": False,
        "with_coreml": False,
        "coreml_allow_fallback": False,
        "with_blas": False,
        "with_openvino": False,
    }
    package_type = "library"

    @property
    def _min_cppstd(self):
        return "14"

    @property
    def _compilers_minimum_version(self):
        return {
            "14": {
                "gcc": "9",
                "clang": "5",
                "apple-clang": "10",
                "Visual Studio": "15",
                "msvc": "191",
            },
        }.get(self._min_cppstd, {})

    @property
    def _is_metal_option_available(self):
        return is_apple_os(self) and Version(self.version) >= "1.5.2"

    @property
    def _is_openvino_option_available(self):
        return Version(self.version) >= "1.5.2"

    def config_options(self):
        if is_apple_os(self):
            del self.options.with_blas
        else:
            del self.options.no_accelerate
            del self.options.with_coreml
            del self.options.coreml_allow_fallback

        if self.settings.os == "Windows":
            del self.options.fPIC

        if not self._is_metal_option_available:
            del self.options.metal
            del self.options.metal_ndebug

        if not self._is_openvino_option_available:
            del self.options.with_openvino

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

        if is_apple_os(self):
            if not self.options.with_coreml:
                self.options.rm_safe("coreml_allow_fallback")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def requirements(self):
        if not is_apple_os(self):
            if self.options.with_blas:
                self.requires("openblas/0.3.24")
        if self.options.get_safe("with_openvino"):
            self.requires("openvino/2023.2.0")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.set_property("openblas", "cmake_file_name", "BLAS")
        deps.generate()

        tc = CMakeToolchain(self)
        tc.variables["WHISPER_BUILD_TESTS"] = False
        tc.variables["WHISPER_BUILD_EXAMPLES"] = False

        if self.options.shared:
            tc.variables["BUILD_SHARED_LIBS"] = True
        if self.options.sanitize_thread:
            tc.variables["WHISPER_SANITIZE_THREAD"] = True
        if self.options.sanitize_address:
            tc.variables["WHISPER_SANITIZE_ADDRESS"] = True
        if self.options.sanitize_undefined:
            tc.variables["WHISPER_SANITIZE_UNDEFINED"] = True
        if self.options.no_avx:
            tc.variables["WHISPER_NO_AVX"] = True
        if self.options.no_avx2:
            tc.variables["WHISPER_NO_AVX2"] = True
        if self.options.no_fma:
            tc.variables["WHISPER_NO_FMA"] = True
        if self.options.no_f16c:
            tc.variables["WHISPER_NO_F16C"] = True

        if self.options.get_safe("with_openvino"):
            tc.variables["WHISPER_OPENVINO"] = True
            # TODO: remove with Conan 1.x support
            tc.variables["CMAKE_CXX_STANDARD"] = str(self.settings.get_safe("compiler.cppstd", 11)).replace("gnu", "")

        if is_apple_os(self):
            if self.options.no_accelerate:
                tc.variables["WHISPER_NO_ACCELERATE"] = True
            if not self.options.get_safe("metal"):
                tc.variables["WHISPER_METAL"] = False
            if self.options.get_safe("metal_ndebug"):
                tc.variables["WHISPER_METAL_NDEBUG"] = True
            if self.options.with_coreml:
                tc.variables["WHISPER_COREML"] = True
                if self.options.coreml_allow_fallback:
                    tc.variables["WHISPER_COREML_ALLOW_FALLBACK"] = True
            if self._is_metal_option_available:
                tc.variables["WHISPER_METAL"] = self.options.metal
        else:
            if self.options.with_blas:
                if Version(self.version) >= "1.4.2":
                    tc.variables["WHISPER_OPENBLAS"] = True
                else:
                    tc.variables["WHISPER_SUPPORT_OPENBLAS"] = True

        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        copy(self, "*", os.path.join(self.source_folder, "models"), os.path.join(self.package_folder, "res", "models"))

    def package_info(self):
        self.cpp_info.libs = ["whisper"]
        self.cpp_info.resdirs = ["res"]
        self.cpp_info.libdirs = ["lib", "lib/static"]

        if self.options.get_safe("with_openvino"):
            self.cpp_info.requires = ["openvino::Runtime"]

        if is_apple_os(self):
            if not self.options.no_accelerate:
                self.cpp_info.frameworks.append("Accelerate")
            if self.options.with_coreml:
                self.cpp_info.frameworks.append("CoreML")
            if self.options.get_safe("metal"):
                self.cpp_info.frameworks.extend(["CoreFoundation", "Foundation", "Metal", "MetalKit"])
        elif self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.extend(["dl", "m", "pthread"])
