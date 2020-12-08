from conans import ConanFile, CMake, tools
from fnmatch import fnmatch
import os


class MgsConan(ConanFile):
    name = "mgs"
    version = "0.1.1"
    license = "MIT"
    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name, self._source_subfolder)

    def package(self):
        for subfolder in ("include", "lib"):
            self.copy("*",
                      src=os.path.join(self._source_subfolder, subfolder),
                      dst=subfolder)
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
