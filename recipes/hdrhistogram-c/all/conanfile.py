from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class QuickfixConan(ConanFile):
    name = "hdrhistogram-c"
    license = "BSD 2-Clause License"
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
    generators = "cmake"
    exports_sources = "patches/**"
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
            if self.options.shared:
                self._cmake.definitions["HDR_HISTOGRAM_BUILD_SHARED"] = True
                self._cmake.definitions["HDR_HISTOGRAM_INSTALL_SHARED"] = True
                self._cmake.definitions["HDR_HISTOGRAM_BUILD_STATIC"] = False
                self._cmake.definitions["HDR_HISTOGRAM_INSTALL_STATIC"] = False
            else:
                self._cmake.definitions["HDR_HISTOGRAM_BUILD_SHARED"] = False
                self._cmake.definitions["HDR_HISTOGRAM_INSTALL_SHARED"] = False
                self._cmake.definitions["HDR_HISTOGRAM_BUILD_STATIC"] = True
                self._cmake.definitions["HDR_HISTOGRAM_INSTALL_STATIC"] = True
            self._cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._cmake

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("HdrHistogram_c-" + self.version, self._source_subfolder)

    def requirements(self):
        pass

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        pass

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = [os.path.join("include", "hdr")]
