from conan import ConanFile, tools$
import os

required_conan_version = ">=1.33.0"


class DecimalforcppConan(ConanFile):
    name = "decimal_for_cpp"
    description = "Decimal data type support, for COBOL-like fixed-point operations on currency values."
    license = "BSD-3-Clause"
    topics = ("decimal_for_cpp", "currency", "money-library", "decimal-numbers")
    homepage = "https://github.com/vpiotr/decimal_for_cpp"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("license.txt", dst="licenses", src=os.path.join(self._source_subfolder, "doc"))
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
