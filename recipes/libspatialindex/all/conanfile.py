import os

from conan import ConanFile, tools
from conans import CMake

class LibspatialindexConan(ConanFile):
    name = "libspatialindex"
    description = "C++ implementation of R*-tree, an MVR-tree and a TPR-tree with C API."
    license = "MIT"
    topics = ("conan", "libspatialindex", "spatial-indexing", "tree")
    homepage = "https://github.com/libspatialindex/libspatialindex"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
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

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["SIDX_BUILD_TESTS"] = False
        self._cmake.definitions["SIDX_BIN_SUBDIR"] = "bin"
        self._cmake.definitions["SIDX_LIB_SUBDIR"] = "lib"
        self._cmake.definitions["SIDX_INCLUDE_SUBDIR"] = "include"
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        suffix = self._get_lib_suffix()
        self.cpp_info.components["spatialindex"].libs = ["spatialindex" + suffix]
        if self.settings.os == "Linux":
            self.cpp_info.components["spatialindex"].system_libs.append("m")
        self.cpp_info.components["spatialindex_c"].libs = ["spatialindex_c" + suffix]
        self.cpp_info.components["spatialindex_c"].requires = ["spatialindex"]
        if not self.options.shared and tools.stdcpp_library(self):
            self.cpp_info.components["spatialindex"].system_libs.append(tools.stdcpp_library(self))
            self.cpp_info.components["spatialindex_c"].system_libs.append(tools.stdcpp_library(self))
        if not self.options.shared and self.settings.compiler == "Visual Studio":
            self.cpp_info.components["spatialindex"].defines.append("SIDX_STATIC")
            self.cpp_info.components["spatialindex_c"].defines.append("SIDX_STATIC")

    def _get_lib_suffix(self):
        suffix = ""
        if self.settings.compiler == "Visual Studio":
            libs = tools.collect_libs(self)
            for lib in libs:
                if "spatialindex_c" in lib:
                    suffix = lib.split("spatialindex_c", 1)[1]
                    break
        return suffix
