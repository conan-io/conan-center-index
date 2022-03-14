from conans import ConanFile, CMake, tools
import functools
import os

required_conan_version = ">=1.33.0"


class LaszipConan(ConanFile):
    name = "laszip"
    description = "C++ library for lossless LiDAR compression."
    license = "LGPL-2.1"
    topics = ("laszip", "las", "laz", "lidar", "compression", "decompression")
    homepage = "https://github.com/LASzip/LASzip"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        # Do not build laszip_api, only laszip
        tools.replace_in_file(os.path.join(self._source_subfolder, "dll", "CMakeLists.txt"),
                              "LASZIP_ADD_LIBRARY(${LASZIP_API_LIB_NAME} ${LASZIP_API_SOURCES})", "")
        cmake = self._configure_cmake()
        cmake.build()

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["LASZIP_BUILD_STATIC"] = not self.options.shared
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["laszip"]
        if self.options.shared:
            self.cpp_info.defines.append("LASZIP_DYN_LINK")
        else:
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.append("m")
            libcxx = tools.stdcpp_library(self)
            if libcxx:
                self.cpp_info.system_libs.append(libcxx)
