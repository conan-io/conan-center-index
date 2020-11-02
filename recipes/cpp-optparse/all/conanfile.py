from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil


class CppOptparse(ConanFile):
    name = "cpp-optparse"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/weisslj/cpp-optparse"
    description = "Python's excellent OptionParser in C++"
    topics = ("conan", "utils", "library")
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False],
               "shared": [True, False]}
    default_options = {"fPIC": True,
                       "shared": False}
    generators = "cmake"
    exports_sources = ["CMakeLists.txt"]
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("cpp-optparse-" + self.version,
            self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def build(self):
        self._patch()

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
