import os

from conans import ConanFile, CMake, tools

class GeosConan(ConanFile):
    name = "geos"
    description = "C++11 library for performing operations on two-dimensional vector geometries"
    license = "LGPL-2.1"
    topics = ("conan", "geos", "osgeo", "geometry", "topology", "geospatial")
    homepage = "https://trac.osgeo.org/geos"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "inline": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "inline": True
    }

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
        os.rename(self.name, self._source_subfolder)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def _patch_sources(self):
        cmakelists_path = os.path.join(self._source_subfolder, "CMakeLists.txt")
        tools.replace_in_file(cmakelists_path, "cmake_minimum_required(VERSION 3.13 FATAL_ERROR)", "")
        tools.replace_in_file(cmakelists_path, "add_subdirectory(benchmarks)", "")
        tools.replace_in_file(cmakelists_path, "add_subdirectory(doc)", "")
        tools.replace_in_file(cmakelists_path, "LIBRARY DESTINATION lib NAMELINK_SKIP", "LIBRARY DESTINATION lib")
        tools.replace_in_file(cmakelists_path, "add_subdirectory(tools)", "")
        tools.replace_in_file(cmakelists_path, "find_package(MakeDistCheck)", "")
        tools.replace_in_file(cmakelists_path, "AddMakeDistCheck()", "")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["DISABLE_GEOS_INLINE"] = not self.options.inline
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("geos.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
        if self.options.inline:
            self.copy(pattern="*.inl", dst="include", src=os.path.join(self._source_subfolder, "include"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["geos_c", "geos"]
        if self.options.inline:
            self.cpp_info.defines.append("GEOS_INLINE")
        self.cpp_info.names["cmake_find_package"] = "GEOS"
        self.cpp_info.names["cmake_find_package_multi"] = "GEOS"
