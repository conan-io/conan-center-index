import os
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration, ConanException


class ConanRecipe(ConanFile):
    name = "serial"
    description = "Cross-platform library for interfacing with rs-232 serial like ports"
    topics = ("serial", "rs-232", "com")
    homepage = "http://wjwwood.io/serial/"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    exports_sources = ["CMakeLists.txt", "Findcatkin.cmake"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

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

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version),
                  self._source_subfolder)

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
        self.copy("README.md", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["serial"]

        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["rt", "pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["setupapi"]
        elif tools.is_apple_os(self.settings.os):
            self.cpp_info.frameworks = ["IOKit", "Foundation"]
