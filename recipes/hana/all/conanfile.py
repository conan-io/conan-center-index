import os
from conans import ConanFile, tools, CMake

class eigenConan(ConanFile):
    name = "hana"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://boostorg.github.io/hana/"
    description = "Hana is a header-only library for C++ metaprogramming suited for computations on both types and values."
    license = "BSL-1.0"
    topics = ("hana", "metaprogramming", "boost")
    settings = "os", "compiler"
    no_copy_source = True
    exports_sources = "CMakeLists.txt"

    @property
    def _source_subfolder(self):
        return "_source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("hana-" + self.version, self._source_subfolder)

    def package(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder)
        cmake.install()

        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
