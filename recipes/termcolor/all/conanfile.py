import os
from conans import ConanFile, tools


class TermcolorConan(ConanFile):
    name = "termcolor"
    homepage = "https://github.com/ikalnytskyi/termcolor"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Termcolor is a header-only C++ library for printing colored messages to the terminal."
    license = "BSD-3-Clause"
    topics = ("conan", "termcolor", "terminal", "color")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy(pattern="*.h", src=os.path.join(self._source_subfolder, "include"), dst="include")
        self.copy(pattern="*.hpp", src=os.path.join(self._source_subfolder, "include"), dst="include")
