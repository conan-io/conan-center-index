import os
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.28.0"

class GeosConan(ConanFile):
    name = "geos"
    description = "C++11 library for performing operations on two-dimensional vector geometries"
    license = "LGPL-2.1"
    topics = ("conan", "geos", "osgeo", "geometry", "topology", "geospatial")
    homepage = "https://trac.osgeo.org/geos"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/*"]
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

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name, self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, {}):
            tools.patch(**patch)

        if self.settings.os == "Macos" and self.settings.arch == "armv8" and tools.Version(self.version) <= "3.9.0":
            # Issue reported https://trac.osgeo.org/geos/ticket/1090, and 
            # fixed upstream for following versions https://trac.osgeo.org/geos/changeset/6318f224552c27a4b87ecf8817173cb7e6a2f4f1/git
            os.unlink(os.path.join(self.build_folder, self._source_subfolder, 'src', 'inlines.cpp'))

        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if tools.Version(self.version) >= "3.9.1":
            self._cmake.definitions["BUILD_BENCHMARKS"] = False
        self._cmake.definitions["DISABLE_GEOS_INLINE"] = not self.options.inline
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("geos.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "geos"
        self.cpp_info.filenames["cmake_find_package_multi"] = "geos"
        self.cpp_info.names["cmake_find_package"] = "GEOS"
        self.cpp_info.names["cmake_find_package_multi"] = "GEOS"
        # GEOS::geos_cxx_flags
        self.cpp_info.components["geos_cxx_flags"].defines.append("USE_UNSTABLE_GEOS_CPP_API")
        if self.options.inline:
            self.cpp_info.components["geos_cxx_flags"].defines.append("GEOS_INLINE")
        if self.settings.os == "Windows":
            self.cpp_info.components["geos_cxx_flags"].defines.append("TTMATH_NOASM")
        # GEOS::geos
        self.cpp_info.components["geos_cpp"].names["cmake_find_package"] = "geos"
        self.cpp_info.components["geos_cpp"].names["cmake_find_package_multi"] = "geos"
        self.cpp_info.components["geos_cpp"].libs = ["geos"]
        if self.settings.os == "Linux":
            self.cpp_info.components["geos_cpp"].system_libs.append("m")
        if not self.options.shared and tools.stdcpp_library(self):
            self.cpp_info.components["geos_cpp"].system_libs.append(tools.stdcpp_library(self))
        self.cpp_info.components["geos_cpp"].requires = ["geos_cxx_flags"]
        # GEOS::geos_c
        self.cpp_info.components["geos_c"].libs = ["geos_c"]
        self.cpp_info.components["geos_c"].requires = ["geos_cpp"]
