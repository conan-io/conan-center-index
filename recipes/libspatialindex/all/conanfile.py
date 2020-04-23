import os

from conans import ConanFile, CMake, tools

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
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
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
        self.cpp_info.libs = self._get_ordered_libs()
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
        if not self.options.shared and self.settings.compiler == "Visual Studio":
            self.cpp_info.defines.append("SIDX_STATIC")

    def _get_ordered_libs(self):
        ordered_libs = ["spatialindex_c", "spatialindex"]
        # With Visual Studio, libspatialindex adds -32 or -64 suffix depending on pointer size
        if self.settings.compiler == "Visual Studio":
            suffix = ""
            libs = tools.collect_libs(self)
            for lib in libs:
                if "spatialindex_c" in lib:
                    suffix = lib.split("spatialindex_c", 1)[1]
                    break
            ordered_libs = [lib + suffix for lib in ordered_libs]
        return ordered_libs
