import os

from conans import ConanFile, CMake, tools

class H3Conan(ConanFile):
    name = "h3"
    description = "Hexagonal hierarchical geospatial indexing system."
    license = "Apache-2.0"
    topics = ("conan", "h3", "hierarchical", "geospatial", "indexing")
    homepage = "https://github.com/uber/h3"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "h3_prefix": "ANY"
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "h3_prefix": ""
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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["H3_PREFIX"] = self.options.h3_prefix
        self._cmake.definitions["ENABLE_COVERAGE"] = False
        self._cmake.definitions["BUILD_BENCHMARKS"] = False
        self._cmake.definitions["BUILD_FILTERS"] = False
        self._cmake.definitions["BUILD_GENERATORS"] = False
        self._cmake.definitions["WARNINGS_AS_ERRORS"] = False
        self._cmake.definitions["ENABLE_LINTING"] = False
        self._cmake.definitions["ENABLE_DOCS"] = False
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.defines.append("H3_PREFIX={}".format(self.options.h3_prefix))
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
        self.cpp_info.names["cmake_find_package"] = "h3"
        self.cpp_info.names["cmake_find_package_multi"] = "h3"
