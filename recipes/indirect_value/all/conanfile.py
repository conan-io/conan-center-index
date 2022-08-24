from conan import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class IndirectValueConan(ConanFile):
    name = "indirect_value"
    homepage = "https://github.com/jbcoe/indirect_value"
    description = "Production-quality reference implementation of P1950: A Free-Store-Allocated Value Type For C++"
    topics = ("std", "vocabulary-type", "value-semantics")
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "gcc": "8",
            "clang": "8",
            "apple-clang": "11"
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(
            str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} "
                             "compiler support.".format(
                                 self.name, self.settings.compiler))
        else:
            if tools.scm.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(
                    "{} requires C++{} support. "
                    "The current compiler {} {} does not support it.".format(
                        self.name, self._minimum_cpp_standard,
                        self.settings.compiler,
                        self.settings.compiler.version))

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy(pattern="indirect_value.*", dst="include",
                  src=self._source_subfolder)
        self.copy("*LICENSE*", dst="licenses", keep_path=False)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "indirect_value")
        self.cpp_info.set_property("cmake_target_name", "indirect_value::indirect_value")

        self.cpp_info.names["cmake_find_package"] = "indirect_value"
        self.cpp_info.names["cmake_find_package_multi"] = "indirect_value"
