from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os


required_conan_version = ">=1.33.0"

class IntelNeon2sseConan(ConanFile):
    name = "intel-neon2sse"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/intel/ARM_NEON_2_x86_SSE"
    description = "Header only library intended to simplify ARM->IA32 porting"
    license = "BSD-2-Clause"
    topics = "neon", "sse", "port", "translation", "intrinsics"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    exports_sources = "CMakeLists.txt"
    options = {
        "SSE4": [True, False],
        "disable_performance_warnings": [True, False],
    }
    default_options = {
        "SSE4": False,
        "disable_performance_warnings": False,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def validate(self):
        if self.settings.arch not in ("x86", "x86_64"):
            raise ConanInvalidConfiguration("neon2sse only supports arch={x86,x86_64}")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "lib"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.names["cmake_find_package"] = "NEON_2_SSE"
        self.cpp_info.names["cmake_find_package_multi"] = "NEON_2_SSE"
        if self.options.SSE4:
            self.cpp_info.defines.append("USE_SSE4")
        if self.options.disable_performance_warnings:
            self.cpp_info.defines.append("NEON2SSE_DISABLE_PERFORMANCE_WARNING")
