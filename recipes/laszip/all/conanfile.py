import os

from conans import ConanFile, CMake, tools

class LaszipConan(ConanFile):
    name = "laszip"
    description = "C++ library for lossless LiDAR compression."
    license = "LGPL-2.1"
    topics = ("conan", "laszip", "las", "laz", "lidar", "compression", "decompression")
    homepage = "https://github.com/LASzip/LASzip"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("LASzip-" + self.version, self._source_subfolder)

    def build(self):
        # Do not build laszip_api, only laszip
        tools.replace_in_file(os.path.join(self._source_subfolder, "dll", "CMakeLists.txt"),
                              "LASZIP_ADD_LIBRARY(${LASZIP_API_LIB_NAME} ${LASZIP_API_SOURCES})", "")
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["LASZIP_BUILD_STATIC"] = not self.options.shared
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.options.shared:
            self.cpp_info.defines.append("LASZIP_DYN_LINK")
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]
