import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class CozConan(ConanFile):
    name = "coz"
    description = """Causal profiler, uses performance experiments
                     to predict the effect of optimizations"""
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://coz-profiler.org"
    license = "BSD-2-Clause"
    topics = ("conan", "coz", "profiler", "causal")

    settings = "os", "arch", "compiler", "build_type"

    requires = "libelfin/0.3"
    exports_sources = "CMakeLists.txt", "patches/*"
    generators = "cmake"

    _cmake = None
    _source_subfolder = "source_subfolder"

    def configure(self):
        if self.settings.os == "Macos" or self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration(
                "coz doesn't support compiler: {} on OS: {}.".format(
                    self.settings.compiler, self.settings.os))
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Coz"
        self.cpp_info.syslibs = ["dl", "rt"]
        if self.settings.os != "Windows":
            self.cpp_info.system_libs = [
                "-Wl,--push-state,--no-as-needed", "-ldl", "-Wl,--pop-state"
            ]
