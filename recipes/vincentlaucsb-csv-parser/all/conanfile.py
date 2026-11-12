import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, download, get, load, save
from conan.tools.scm import Version
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class VincentlaucsbCsvParserConan(ConanFile):
    name = "vincentlaucsb-csv-parser"
    description = "Vince's CSV Parser with simple and intuitive syntax"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/vincentlaucsb/csv-parser"
    topics = ("csv", "rfc 4180", "parser", "generator", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 14)

    def source(self):
        if Version(self.version) >= Version("2.5.2"):
            download(self, **self.conan_data["sources"][self.version], filename="csv.hpp")
        else:
            get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _extract_license(self):
        # The MIT license text is embedded in the header's leading comment
        header = load(self, os.path.join(self.source_folder, "csv.hpp"))
        start = header.index("MIT License")
        end = header.index("*/", start)
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), header[start:end].strip() + "\n")

    def package(self):
        if Version(self.version) >= Version("2.5.2"):
            self._extract_license()
            copy(self, "csv.hpp",
                 dst=os.path.join(self.package_folder, "include"),
                 src=self.source_folder)
        else:
            copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
            copy(self, pattern="*",
                 dst=os.path.join(self.package_folder, "include"),
                 src=os.path.join(self.source_folder, "single_include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.append("pthread")
