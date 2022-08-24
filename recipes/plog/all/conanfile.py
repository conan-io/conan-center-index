import os
from conans import ConanFile, tools


class PlogConan(ConanFile):
    name = "plog"
    description = "Pretty powerful logging library in about 1000 lines of code"
    homepage = "https://github.com/SergiusTheBest/plog"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MPL-2.0"
    topics = ("logging", "header-only", "portable")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", src=os.path.join(self._source_subfolder, "include"), dst=os.path.join("include"))

    def package_id(self):
        self.info.header_only()
