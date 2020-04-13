import os
from conans import ConanFile, tools

class Tabulate(ConanFile):
    name = "tabulate"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/p-ranav/tabulate"
    description = "Table Maker for Modern C++"
    topics = ("conan", "cpp17", "tabulate")
    license = "MIT"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
