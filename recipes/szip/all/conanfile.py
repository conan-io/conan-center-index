import os

from conans import ConanFile, CMake, tools

class SzipConan(ConanFile):
    name = "szip"
    description = "C Implementation of the extended-Rice lossless compression " \
                  "algorithm, suitable for use with scientific data."
    license = "Szip License"
    topics = ("conan", "szip", "compression", "decompression")
    homepage = "https://support.hdfgroup.org/doc_resource/SZIP/"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_encoding": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_encoding": False
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
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "set (CMAKE_POSITION_INDEPENDENT_CODE ON)", "")
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["SZIP_ENABLE_ENCODING"] = self.options.enable_encoding
        self._cmake.definitions["SZIP_EXTERNALLY_CONFIGURED"] = True
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["SZIP_BUILD_FRAMEWORKS"] = False
        self._cmake.definitions["SZIP_PACK_MACOSX_FRAMEWORK"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "SZIP"
        self.cpp_info.names["cmake_find_package_multi"] = "SZIP"

        self.cpp_info.libs = tools.collect_libs(self)
