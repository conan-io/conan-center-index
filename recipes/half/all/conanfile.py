from conan import ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class HalfConan(ConanFile):
    name = "half"
    description = (
        "C++ header-only library to provide an IEEE 754 conformant 16-bit "
        "half-precision floating-point type along with corresponding "
        "arithmetic operators, type conversions and common mathematical "
        "functions."
    )
    license = "MIT"
    topics = ("half", "half-precision", "float", "arithmetic")
    homepage = "https://sourceforge.net/projects/half"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder)

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy("half.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
