import os
from conans import ConanFile, tools

required_conan_version = ">=1.43.0"


class FastDoubleParserConan(ConanFile):
    name = "fast_double_parser"
    description = "Fast function to parse strings into double (binary64) floating-point values, enforces the RFC 7159 (JSON standard) grammar: 4x faster than strtod"
    topics = ("numerical", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lemire/fast_double_parser"
    license = ("Apache-2.0", "BSL-1.0")

    settings = "os", "compiler", "build_type", "arch"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        include_folder = os.path.join(self._source_subfolder, "include")
        self.copy("*.h", dst="include", src=include_folder)
        self.copy("LICENSE*", dst="licenses", src=self._source_subfolder)
