import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

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
    exports_sources = "CMakeLists.txt", "patches/*"
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
            tools.check_min_cppstd(self, "11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    __cmake = None

    @property
    def _cmake(self):
        if self.__cmake is None:
            self.__cmake = CMake(self)
        return self.__cmake

    def build(self):
        self._cmake.configure()
        self._cmake.build()

    def package(self):
        self._cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "coz-profiler"
        self.cpp_info.filenames["cmake_find_package_multi"] = "coz-profiler"
        self.cpp_info.names["cmake_find_package"] = "coz"
        self.cpp_info.names["cmake_find_package_multi"] = "coz"
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl", "rt", "pthread"]
