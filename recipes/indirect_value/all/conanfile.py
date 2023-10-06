import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class IndirectValueConan(ConanFile):
    name = "indirect_value"
    description = "Production-quality reference implementation of P1950: A Free-Store-Allocated Value Type For C++"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jbcoe/indirect_value"
    topics = ("std", "vocabulary-type", "value-semantics", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "gcc": "8",
            "clang": "8",
            "apple-clang": "11",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warning(f"{self.name} recipe lacks information about the "
                                f"{self.settings.compiler} compiler support.")
        else:
            if Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(
                    f"{self.name} requires C++{self._minimum_cpp_standard} support. The current compiler"
                    f" {self.settings.compiler} {self.settings.compiler.version} does not support it."
                )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "indirect_value.*",
             dst=os.path.join(self.package_folder, "include"),
             src=self.source_folder)
        copy(self, "*LICENSE*",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder,
             keep_path=False)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "indirect_value")
        self.cpp_info.set_property("cmake_target_name", "indirect_value::indirect_value")

        self.cpp_info.names["cmake_find_package"] = "indirect_value"
        self.cpp_info.names["cmake_find_package_multi"] = "indirect_value"
