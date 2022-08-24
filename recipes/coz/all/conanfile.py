import os
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


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
    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package"

    _source_subfolder = "source_subfolder"

    def validate(self):
        compiler = self.settings.compiler
        compiler_version = tools.Version(self.settings.compiler.version)
        if self.settings.os == "Macos" or compiler == "Visual Studio" or (
                compiler == "gcc" and compiler_version < "5.0"):
            raise ConanInvalidConfiguration(
                "coz doesn't support compiler: {} on OS: {}.".format(
                    self.settings.compiler, self.settings.os))
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, self, "11")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    _cmake = None

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "coz-profiler"
        self.cpp_info.filenames["cmake_find_package_multi"] = "coz-profiler"
        self.cpp_info.names["cmake_find_package"] = "coz"
        self.cpp_info.names["cmake_find_package_multi"] = "coz"
