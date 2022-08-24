from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration

import os

required_conan_version = ">=1.33.0"

class PerfettoConan(ConanFile):
    name = "perfetto"
    license = "Apache-2.0"
    homepage = "https://perfetto.dev"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Performance instrumentation and tracing for Android, Linux and Chrome"
    topics = ("linux", "profiling", "tracing")
    settings = "os", "compiler", "build_type", "arch"
    options = {
            "shared": [True, False],
            "fPIC": [True, False],
            "disable_logging": [True, False], # switches PERFETTO_DISABLE_LOG
    }
    default_options = {
            "shared": False,
            "fPIC": True,
            "disable_logging": False,
    }

    short_paths = True
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler == "gcc" and tools.scm.Version(self.settings.compiler.version) < 7:
            raise ConanInvalidConfiguration ("perfetto requires gcc >= 7")
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
               strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if self.options.get_safe("disable_logging", False) == True:
            self._cmake.definitions["PERFETTO_DISABLE_LOGGING"] = True
        self._cmake.configure()
        return self._cmake

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["perfetto"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")

