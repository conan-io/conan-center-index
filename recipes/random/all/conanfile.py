import os

from conans import ConanFile, tools

class RandomConan(ConanFile):
    name = "random"
    description = "Random for modern C++ with convenient API."
    license = "MIT"
    topics = ("conan", "random", "header-only")
    homepage = "https://github.com/effolkronium/random"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def package(self):
        self.copy("LICENSE.MIT", dst="licenses", src=self._source_subfolder)
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_id(self):
        self.info.header_only()

