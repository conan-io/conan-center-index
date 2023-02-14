from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, load, save
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.52.0"

class ExprTkConan(ConanFile):
    name = "exprtk"
    description = "C++ Mathematical Expression Parsing And Evaluation Library ExprTk"
    license = ("MIT")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.partow.net/programming/exprtk/index.html"
    topics = ("math", "mathematics", "parser", "lexer", "numerical", "header-only")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _extract_license(self):
        source_file = os.path.join(self.source_folder, self.source_folder, "exprtk.hpp")
        file_content = load(self, source_file)
        license_end = "/MIT                        *"
        license_contents = file_content[2:file_content.find(license_end) + len(license_end)]
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_contents)

    def package(self):
        self._extract_license()
        copy(
            self,
            pattern="exprtk.hpp",
            dst=os.path.join(self.package_folder, "include"),
            src=self.source_folder,
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
