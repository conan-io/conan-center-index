from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.layout import basic_layout
from conan.tools.files import get, copy, load, save
import os

required_conan_version = ">=1.53.0"


class ExprTkConan(ConanFile):
    name = "exprtk"
    description = "C++ Mathematical Expression Parsing And Evaluation Library ExprTk"
    license = "MIT"
    topics = ("math", "mathematics", "parser", "lexer", "numerical", "header-only")
    homepage = "https://www.partow.net/programming/exprtk/index.html"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 11

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _extract_license(self):
        exprtk_header_file = "exprtk.hpp"
        file = os.path.join(self.source_folder, exprtk_header_file)
        file_content = load(self, file)
        license_end = "/MIT                        *"
        license_contents = file_content[2:file_content.find(license_end) + len(license_end)]
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_contents)

    def package(self):
        self._extract_license()
        copy(self, "exprtk.hpp", dst=os.path.join(self.package_folder, "include"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
