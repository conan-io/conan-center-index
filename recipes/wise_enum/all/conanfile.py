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
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSL-1.0"
    settings = "compiler"
    no_copy_source = True
    
    @property
    def _source_subfolder(self):
        return "source_subfolder"    
   

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "11")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)
        if self.settings.compiler == "Visual Studio":
            with tools.chdir(self._source_subfolder):
                self.run("{} create_generated.py 125  wise_enum_generated.h".format(self._python_executable))
        

    def package(self):
        self.copy("*.h", dst="include", src=self._source_subfolder)
        self.copy("LICENSE", dst="licenses" , src=self._source_subfolder)
        
    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "wise_enum"
        self.cpp_info.names["cmake_find_package_multi"] = "wise_enum"

