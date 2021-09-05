from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"

class WiseEnumConan(ConanFile):
    name = "wise_enum"
    description = "Header-only C++11/14/17 library provides static reflection for enums, work with any enum type without any boilerplate code."
    topics = (
        "cplusplus",
        "enum-to-string",
        "string-to-enum"
        "serialization",
        "reflection",
        "header-only",
        "compile-time"
    )
    homepage = "https://github.com/quicknir/wise_enum"
    url = "https://github.com/conan-io/conan-center-index/"
    homepage = url
    license = "BPL"
    settings = "compiler"
    no_copy_source = True
    
    @property
    def _source_subfolder(self):
        return "source_subfolder"    
   

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "11")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("*.h", dst="include", src=self._source_subfolder)
        self.copy("LICENSE", dst="licenses" , src=self._source_subfolder)
