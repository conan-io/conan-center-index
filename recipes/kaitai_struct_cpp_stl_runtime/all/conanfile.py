import os

from conan import ConanFile, tools
from conan.tools.cmake import CMake


class KaitaiStructCppStlRuntimeConan(ConanFile):
    name = "kaitai_struct_cpp_stl_runtime"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://kaitai.io/"
    description = "kaitai struct c++ runtime library"
    topics = ("parsers", "streams", "dsl")
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    options = {
        "with_zlib": [True, False],
        "with_iconv": [True, False]
    }
    default_options = {
        "with_zlib": False,
        "with_iconv": False
    }
    short_paths = True
    _cmake = None

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.with_iconv:
            self.requires("libiconv/1.16")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        if self.options.with_iconv:
            self._cmake.definitions["STRING_ENCODING_TYPE"] = "ICONV"
        else:
            self._cmake.definitions["STRING_ENCODING_TYPE"] = "NONE"

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
