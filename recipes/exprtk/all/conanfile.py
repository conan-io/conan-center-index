import os
from conan import ConanFile, tools

required_conan_version = ">=1.33.0"


class ExprTkConan(ConanFile):
    name = "exprtk"
    description = "C++ Mathematical Expression Parsing And Evaluation Library ExprTk"
    license = ("MIT")
    topics = ("exprtk", "cpp", "math", "mathematics", "parser", "lexer", "numerical")
    homepage = "https://www.partow.net/programming/exprtk/index.html"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, 11)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _extract_license(self):
        exprtk_header_file = "exprtk.hpp"
        file = os.path.join(self.source_folder, self._source_subfolder, exprtk_header_file)
        file_content = tools.files.load(self, file)
        license_end = "/MIT                        *"
        license_contents = file_content[2:file_content.find(license_end) + len(license_end)]
        tools.files.save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_contents)

    def package(self):
        self._extract_license()
        self.copy("exprtk.hpp", dst="include" , src=self._source_subfolder)
