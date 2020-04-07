from conans import ConanFile, CMake, tools
from fnmatch import fnmatch
import os


class TlConan(ConanFile):
    name = "tl"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://tl.tartanllama.xyz"
    description = "tl is a collection of generic C++ libraries"
    topics = ("conan", "c++", "utilities")
    license = "CC0-1.0"
    no_copy_source = True
    _source_subfolder = "tl"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("tl-%s" % self.version, self._source_subfolder)

    def package(self):
        self.copy("*.hpp",
                  src=os.path.join(self._source_subfolder, "include"),
                  dst="include")
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")

    def package_id(self):
        self.info.header_only()
