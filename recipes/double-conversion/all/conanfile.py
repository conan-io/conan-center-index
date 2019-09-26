# -*- coding: utf-8 -*-
import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version


class DoubleConversionConan(ConanFile):
    name = "double-conversion"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/double-conversion"
    description = "Efficient binary-decimal and decimal-binary conversion routines for IEEE doubles."
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "BSD-3-Clause"
    topics = ("conan", "double-conversion", "google", "decimal-binary", "conversion")
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.os == "Windows" and \
            self.settings.compiler == "Visual Studio" and \
            Version(self.settings.compiler.version.value) < "14":
            raise ConanInvalidConfiguration("Double Convertion could not be built by MSVC <14")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib","cmake"))
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
