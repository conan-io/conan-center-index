import os
from conan import ConanFile, tools

required_conan_version = ">=1.33.0"

class VisitStructConan(ConanFile):
    name = "visit_struct"
    description = "A miniature library for struct-field reflection in C++"
    topics = ("reflection", "introspection", "visitor", "struct-field-visitor",)
    homepage = "https://github.com/garbageslam/visit_struct"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSL-1.0"
    settings = "os", "arch", "compiler", "build_type",
    options = {
        "with_boost_fusion": [True, False],
        "with_boost_hana": [True, False],
    }
    default_options = {
        "with_boost_fusion": False,
        "with_boost_hana": False,
    }
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        if self.options.with_boost_fusion or self.options.with_boost_hana:
            self.requires("boost/1.78.0")

    def package_id(self):
        self.info.header_only()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, "11")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy(pattern="*visit_struct.hpp", src=os.path.join(self._source_subfolder, "include"), dst="include")
        self.copy(pattern="*visit_struct_intrusive.hpp", src=os.path.join(self._source_subfolder, "include"), dst="include")
        if self.options.with_boost_fusion:
            self.copy(pattern="*visit_struct_boost_fusion.hpp", src=os.path.join(self._source_subfolder, "include"), dst="include")
        if self.options.with_boost_hana:
            self.copy(pattern="*visit_struct_boost_hana.hpp", src=os.path.join(self._source_subfolder, "include"), dst="include")
