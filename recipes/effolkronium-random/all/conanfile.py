import os

from conan import ConanFile, tools

class RandomConan(ConanFile):
    name = "effolkronium-random"
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
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("random-" + self.version, self._source_subfolder)

    def package(self):
        self.copy("LICENSE.MIT", dst="licenses", src=self._source_subfolder)
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "effolkronium_random"
        self.cpp_info.names["cmake_find_package_multi"] = "effolkronium_random"
