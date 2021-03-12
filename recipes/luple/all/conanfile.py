import os
from conans import ConanFile, CMake, tools


class LupleConan(ConanFile):
    name = "luple"
    license = "Unlicense"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/alexpolt/luple"
    description = "Home to luple, nuple, C++ String Interning, Struct Reader and C++ Type Loophole"
    topics = ("conan", "loophole", "luple", "nuple", "struct", "intern")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        tools.save(os.path.join(self.package_folder, "licenses", "COPYING"), "Public Domain")
        self.copy("*.h", dst="include", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.libdirs = []
