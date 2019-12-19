import os
from conans import ConanFile, tools


class ClaraConan(ConanFile):
    name = "clara"
    description = "A simple to use, composable, command line parser for C++ 11 and beyond"
    homepage = "https://github.com/catchorg/Clara"
    topics = ("conan", "clara", "cli", "cpp11", "command-parser")
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSL-1.0"
    no_copy_source = True

    _source_subfolder = "source_subfolder"

    def configure(self):
        self.output.warn("clara is unmaintained. Consider updating to lyra/1.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("Clara-{}".format(self.version), self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE.txt", src=self._source_subfolder, dst="licenses")
        self.copy(pattern="*", src=os.path.join(self._source_subfolder, "include"), dst="include", keep_path=True)

    def package_id(self):
        self.info.header_only()
