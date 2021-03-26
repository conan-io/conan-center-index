import os

from conans import ConanFile, CMake, tools

class EdlibConan(ConanFile):
    name = "edlib"
    description = "Lightweight, super fast C/C++ (& Python) library for " \
                  "sequence alignment using edit (Levenshtein) distance."
    license = "MIT"
    topics = ("conan", "edlib", "sequence-alignment", "edit-distance", "levehnstein-distance", "alignment-path")
    homepage = "https://github.com/Martinsos/edlib"
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
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["EDLIB_BUILD_EXAMPLES"] = False
        self._cmake.definitions["EDLIB_BUILD_UTILITIES"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "edlib-{}".format(tools.Version(self.version).major)
        self.cpp_info.libs = ["edlib"]
        if self.options.shared:
            self.cpp_info.defines = ["EDLIB_SHARED"]
        if not self.options.shared and tools.stdcpp_library(self):
            self.cpp_info.system_libs = [tools.stdcpp_library(self)]
