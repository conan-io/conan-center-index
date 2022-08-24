import os
from conan import ConanFile, tools


class Rtmonan(ConanFile):
    name = "rtm"
    description = "Realtime Math"
    topics = ("realtime", "math")
    license = "MIT"
    homepage = "https://github.com/nfrechette/rtm"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "includes"))

    def package_id(self):
        self.info.header_only()
