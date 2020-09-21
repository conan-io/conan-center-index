from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version

import os


class SiConan(ConanFile):
    name = "bertrand"
    license = "LGPLv3"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/bernedom/bertrand"
    description = "A C++ header only library providing a trivial implementation for design by contract."
    topics = ("design by contract", "dbc",
              "cplusplus-library", "cplusplus-17")
    exports_sources = "CMakeLists.txt"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _supports_cpp17(self):
        supported_compilers = [
            ("gcc", "7"), ("clang", "5"), ("apple-clang", "10"), ("Visual Studio", "15.7")]
        compiler = self.settings.compiler
        version = Version(compiler.version)
        return any(compiler == sc[0] and version >= sc[1] for sc in supported_compilers)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["BERTRAND_BUILD_TESTING"] = False
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")
        elif not self._supports_cpp17():
            raise ConanInvalidConfiguration("bertrand requires C++17 support")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "bertrand-{}".format(self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "bertrand"
        self.cpp_info.names["cmake_find_package_multi"] = "bertrand"
