from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os

class MagicEnumConan(ConanFile):
    name = "magic_enum"
    description = "Header-only C++17 library provides static reflection for enums, work with any enum type without any macro or boilerplate code."
    topics = (
        "conan",
        "cplusplus",
        "enum-to-string",
        "string-to-enum"
        "serialization",
        "reflection",
        "header-only",
        "compile-time"
    )
    url = "https://github.com/Neargye/magic_enum"
    homepage = "https://github.com/Neargye/magic_enum"
    license = "MIT"
    settings = "compiler"

    _source_subfolder = "source_subfolder"


    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    @property
    def supported_compiler(self):
        compiler = str(self.settings.compiler)
        version = tools.Version(self.settings.compiler.version)
        if compiler == "Visual Studio" and version >= "15":
            return True
        if compiler == "gcc" and version >= "9":
            return True
        if compiler == "clang" and version >= "5":
            return True
        if compiler == "apple-clang" and version >= "10":
            return True
        return False

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")
        if not self.supported_compiler:
            raise ConanInvalidConfiguration("magic_enum: Unsupported compiler (https://github.com/Neargye/magic_enum#compiler-compatibility).")

    def package(self):
        self.copy("include/*", src=self._source_subfolder)
        self.copy("LICENSE", dst="licenses" , src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()