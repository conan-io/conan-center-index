from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class QuickfixConan(ConanFile):
    name = "hdrhistogram-c"
    license = ("BSD-2-Clause", "CC0-1.0")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/HdrHistogram/HdrHistogram_c"
    description = "'C' port of High Dynamic Range (HDR) Histogram"
    topics = ("libraries", "c", "histogram")
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False],
               "shared": [True, False]}
    default_options = {"fPIC": True,
                       "shared": False}
    requires = "zlib/1.2.11"
    generators = "cmake_find_package"
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
            self._cmake.definitions["HDR_HISTOGRAM_BUILD_PROGRAMS"] = False
            self._cmake.definitions["HDR_HISTOGRAM_BUILD_SHARED"] = self.options.shared
            self._cmake.definitions["HDR_HISTOGRAM_INSTALL_SHARED"] = self.options.shared
            self._cmake.definitions["HDR_HISTOGRAM_BUILD_STATIC"] = not self.options.shared
            self._cmake.definitions["HDR_HISTOGRAM_INSTALL_STATIC"] = not self.options.shared
            self._cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._cmake

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("HdrHistogram_c-" + self.version, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy("COPYING.txt", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = ["include", os.path.join("include", "hdr")]

        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m", "rt"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32"])
