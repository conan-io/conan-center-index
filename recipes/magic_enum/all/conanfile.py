from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
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
    url = "https://github.com/conan-io/conan-center-index "
    homepage = "https://github.com/Neargye/magic_enum"
    license = "MIT"
    settings = "compiler", "arch", "build_type", "os"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9",
            "Visual Studio": "15",
            "clang": "5",
            "apple-clang": "10",
        }

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, "17")
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("magic_enum requires C++17. Your compiler is unknown. Assuming it supports C++17.")
        elif tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("magic_enum: Unsupported compiler: {}-{} "
                                            "(https://github.com/Neargye/magic_enum#compiler-compatibility)."
                                            .format(self.settings.compiler, self.settings.compiler.version))

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE", dst="licenses" , src=self._source_subfolder)
