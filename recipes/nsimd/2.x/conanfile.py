import os
import sys

from conans import ConanFile, CMake, tools

required_conan_version = ">=1.33.0"


class NsimdConan(ConanFile):
    name = "nsimd"
    homepage = "https://github.com/agenium-scale/nsimd"
    description = "Agenium Scale vectorization library for CPUs and GPUs"
    topics = ("hpc", "neon", "cuda", "avx", "simd", "avx2", "sse2", "aarch64", "avx512", "sse42", "rocm", "sve", "neon128")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        # This used only when building the library.
        # Most functionality is header only.
        "simd": [None, "cpu", "sse2", "sse42", "avx", "avx2", "avx512_knl", "avx512_skylake", "neon128", "aarch64", "sve", "sve128", "sve256", "sve512", "sve1024", "sve2048", "cuda", "rocm"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "simd": None
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        # Most of the library is header only.
        # cpp files do not use STL.
        del self.settings.compiler.libcxx

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        defs = {}
        if self.options.simd:
            defs["simd"] = self.options.simd
        if self.settings.arch == "armv7hf":
            defs["NSIMD_ARM32_IS_ARMEL"] = "OFF"
        self._cmake.configure(build_folder=self._build_subfolder, defs=defs)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
