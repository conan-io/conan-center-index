import os
from conans import ConanFile, tools


class XtlConan(ConanFile):
    name = "xtl"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xtensor-stack/xtl"
    description = "The x template library"
    topics = ("conan", "templates", "containers", "algorithms")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = self.name + "-" + self.version
        os.rename(extracted_folder, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
