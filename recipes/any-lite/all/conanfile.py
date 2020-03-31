import os
from conans import ConanFile, tools


class AnyLite(ConanFile):
    name = "any-lite"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/martinmoene/any-lite"
    description = "any lite - Any objects in C++11 and later in a single-file header-only library"
    topics = ("conan", "cpp11", "cpp14", "cpp17", "any", "any-implementations")
    license = "BSL-1.0"
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
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
