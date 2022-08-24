from conan import ConanFile, tools

class FlatbushConan(ConanFile):
    name = "flatbush"
    license = "MIT"
    homepage = "https://github.com/chusitoo/flatbush"
    description = "Flatbush for C++"
    topics = ("header-only", "flatbush", "r-tree", "hilbert", "zero-copy", "spatial-index")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    no_copy_source = True

    def source(self):
       tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses")
        self.copy(pattern="flatbush.h", dst="include")

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        if not tools.valid_min_cppstd(self, "20"):
            self.cpp_info.defines = ["FLATBUSH_SPAN"]
