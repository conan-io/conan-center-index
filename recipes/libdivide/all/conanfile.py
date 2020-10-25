from conans import ConanFile, tools
import os


class LibdivideConan(ConanFile):
    name = "libdivide"
    description = "Header-only C/C++ library for optimizing integer division."
    topics = ("conan", "libdivide", "division", "integer")
    license = ["Zlib", "BSL-1.0"]
    homepage = "http://libdivide.com/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy("libdivide.h", dst="include", src=self._source_subfolder)
