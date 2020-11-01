import os
from conans import ConanFile, tools


class NamedTypeConan(ConanFile):
    name = "namedtype"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/joboccara/NamedType"
    description = "Implementation of strong types in C++"
    topics = ("strong types",)
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        url = self.conan_data["sources"][self.version]["url"]
        if self.version == "20190324":
            # non-release version
            extracted_dir = "NamedType-" + os.path.splitext(os.path.basename(url))[0]
        else:
            extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("*.hpp", dst="include", src=self._source_subfolder, keep_path=False)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
