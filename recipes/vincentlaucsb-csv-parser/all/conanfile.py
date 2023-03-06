from conan import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

import os

required_conan_version = ">=1.33.0"

class VincentlaucsbCsvParserConan(ConanFile):
    name = "vincentlaucsb-csv-parser"
    description = "Vince's CSV Parser with simple and intuitive syntax"
    topics = ("conan", "csv-parser", "csv", "rfc 4180", "parser", "generator")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/vincentlaucsb/csv-parser"
    license = "MIT"
    settings = "os", "compiler"
    no_copy_source = True

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            tools.build.check_min_cppstd(self, 11)

        compiler = self.settings.compiler
        compiler_version = tools.scm.Version(self.settings.compiler.version)

        if compiler == "gcc" and compiler_version < "7":
            raise ConanInvalidConfiguration("gcc version < 7 not supported")

    def package_id(self):
        self.info.clear()
        
    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="*", src=os.path.join(self.source_folder, "single_include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.append("pthread")

