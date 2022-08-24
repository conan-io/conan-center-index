from from conan import ConanFile, tools
from conans import CMake
import os


class NaiveTsearchConan(ConanFile):
    name = "naive-tsearch"
    description = "A simple tsearch() implementation for platforms without one"
    topics = ("conan", "naive-tsearch", "tsearch", "search", "tree", "msvc")
    license = "MIT"
    homepage = "https://github.com/kulp/naive-tsearch"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["CMakeLists.txt"]
    options = {
        "fPIC": [True, False],
        "header_only": [True, False],
    }
    default_options = {
        "fPIC": True,
        "header_only": True,
    }
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["NAIVE_TSEARCH_INSTALL"] = True
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_id(self):
        del self.info.options.header_only

    def package_info(self):
        if self.options.header_only:
            self.cpp_info.components["header_only"].libs = []
            self.cpp_info.components["header_only"].libdirs = []
            self.cpp_info.components["header_only"].includedirs.append(os.path.join("include", "naive-tsearch"))
            self.cpp_info.components["header_only"].defines = ["NAIVE_TSEARCH_HDRONLY"]
            self.cpp_info.components["header_only"].names["cmake_find_package"] = "naive-tsearch-hdronly"
            self.cpp_info.components["header_only"].names["cmake_find_package_multi"] = "naive-tsearch-hdronly"
        else:
            self.cpp_info.components["naive_tsearch"].libs = ["naive-tsearch"]
            self.cpp_info.components["naive_tsearch"].includedirs.append(os.path.join("include", "naive-tsearch"))
            self.cpp_info.components["naive_tsearch"].names["cmake_find_package"] = "naive-tsearch"
            self.cpp_info.components["naive_tsearch"].names["cmake_find_package_multi"] = "naive-tsearch"
