import os

from conan import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=1.50.0"


class PolymorphictValueConan(ConanFile):
    name = "polymorphic_value"
    homepage = "https://github.com/jbcoe/polymorphic_value"
    description = "Production-quality reference implementation of P0201r2: A polymorphic value-type for C++"
    topics = ("std", "vocabulary-type", "value-semantics")
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
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
            "apple-clang": "11"
        }

    def validate(self):
        if self.info.settings.get_safe("compiler.cppstd"):
            tools.build.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(
            str(self.info.settings.compiler))
        if not min_version:
            self.output.warning("{} recipe lacks information about the {} "
                                "compiler support.".format(
                                    self.name, self.info.settings.compiler))
        else:
            if tools.Version(self.info.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(
                    "{} requires C++{} support. "
                    "The current compiler {} {} does not support it.".format(
                        self.name, self._minimum_cpp_standard,
                        self.info.settings.compiler,
                        self.info.settings.compiler.version))

    def package_id(self):
        self.info.clear()

    def layout(self):
        basic_layout(self, src_folder="source")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "polymorphic_value.*", self.source_folder,
             os.path.join(self.package_folder, "include"))
        copy(self, "*LICENSE*", self.source_folder,
             os.path.join(self.package_folder, "licenses"), keep_path=False)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "polymorphic_value")
        self.cpp_info.set_property(
            "cmake_target_name", "polymorphic_value::polymorphic_value")

        self.cpp_info.names["cmake_find_package"] = "polymorphic_value"
        self.cpp_info.names["cmake_find_package_multi"] = "polymorphic_value"
