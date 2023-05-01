from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.52.0"

class VisitStructConan(ConanFile):
    name = "visit_struct"
    description = "A miniature library for struct-field reflection in C++"
    license = "BSL-1.0"
    topics = ("reflection", "introspection", "visitor", "struct-field-visitor", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cbeck88/visit_struct"
    package_type = "header-library"
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
    def _min_cppstd(self):
        return 11

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_boost_fusion or self.options.with_boost_hana:
            self.requires("boost/1.81.0")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="*visit_struct.hpp", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))
        copy(self, pattern="*visit_struct_intrusive.hpp", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))
        if self.options.with_boost_fusion:
            copy(self, pattern="*visit_struct_boost_fusion.hpp", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))
        if self.options.with_boost_hana:
            copy(self, pattern="*visit_struct_boost_hana.hpp", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
