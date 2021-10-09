from conans import ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class ItlibConan(ConanFile):
    name = "itlib"
    description = "A collection of small single-header C++ libraries similar to or extending the C++ standard library."
    license = "MIT"
    topics = ("itlib", "template")
    homepage = "https://github.com/iboB/itlib"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
