from conans import ConanFile, CMake, tools
import os

class FlatbushConan(ConanFile):
    name = "flatbush"
    version = "1.0.0"
    # Optional metadata
    license = "MIT"
    homepage = "https://github.com/chusitoo/flatbush"
    description = "Flatbush for C++"
    topics = ("header-only", "flatbush", "r-tree", "hilbert", "zero-copy", "spatial-index")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler"
    #exports_sources = "flatbush.h", "test.cpp", "CMakeLists.txt"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
       tools.get(**self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        cmake.test()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses")
        self.copy(pattern="flatbush.h", dst="include")

    def package_id(self):
        self.info.header_only()

