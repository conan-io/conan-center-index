from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import export_conandata_patches, apply_conandata_patches, copy, get, load, replace_in_file, rmdir, save
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import json
import os
import re
import textwrap

required_conan_version = ">=1.53.0"

required_conan_version = ">=1.33.0"


class WhisperCppConan(ConanFile):
    name = "whisper-cpp"
    description = "High-performance inference of OpenAI's Whisper automatic speech recognition (ASR) model"
    topics = ("whisper", "asr")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ggerganov/whisper.cpp"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "sanitize_thread": [True, False],
               "sanitize_address": [True, False], "sanitize_undefined": [True, False], "with_sdl2": [True, False],
               "no_avx": [True, False], "no_avx2": [True, False], "no_fma": [True, False], "no_f16c": [True, False],
               "on_accelerate": [True, False], "with_coreml": [True, False], "coreml_allow_fallback": [True, False],
               "with_blas": [True, False]}
    default_options = {"shared": False, "fPIC": True, "sanitize_thread": False,
                       "sanitize_address": False, "sanitize_undefined": False, "with_sdl2": False,
                       "no_avx": False, "no_avx2": False, "no_fma": False, "no_f16c": False,
                       "on_accelerate": False, "with_coreml": False, "coreml_allow_fallback": False,
                       "with_blas": False}

    _cmake = None

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

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if is_apple_os(self):
            del self.options.with_blas
        else:
            del self.options.no_accelerate
            del self.options.with_coreml
            del self.options.coreml_allow_fallback

        if self.settings.os == "Windows":
            del self.options.fPIC

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
        if self.options.with_sdl2:
            self.requires("sdl/[>=2.0.0]")

        if not is_apple_os(self):
            if self.options.with_blas:
                self.requires("openblas/[>=0.3.7]")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
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
        if self.options.with_sdl2:
            tc.variables["WHISPER_SDL2"] = True
        if self.options.no_avx:
            tc.variables["WHISPER_NO_AVX"] = True
        if self.options.no_avx2:
            tc.variables["WHISPER_NO_AVX2"] = True
        if self.options.no_fma:
            tc.variables["WHISPER_NO_FMA"] = True
        if self.options.no_f16c:
            tc.variables["WHISPER_NO_F16C"] = True

        if is_apple_os(self):
            if self.options.no_accelerate:
                tc.variables["WHISPER_NO_ACCELERATE"] = True
            if self.options.with_coreml:
                tc.variables["WHISPER_COREML"] = True
            if self.options.coreml_allow_fallback:
                tc.variables["WHISPER_COREML_ALLOW_FALLBACK"] = True
        else:
            if self.options.with_blas:
                tc.variables["WHISPER_BLAS"] = True
                tc.variables["WHISPER_CUBLAS"] = True

        tc.generate()

    def build(self):
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

        if not self.options.shared:
            self.cpp_info.libdirs = ["lib/static"]

        if is_apple_os(self):
            if not self.options.no_accelerate:
                self.cpp_info.frameworks.append("Accelerate")
            if self.options.with_coreml
                self.cpp_info.frameworks.append("CoreML")
