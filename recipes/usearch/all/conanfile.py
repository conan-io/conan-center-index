# To test, please run: conan create all/conanfile.py --version 0.8.0
import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy, export_conandata_patches, apply_conandata_patches
from conan.tools.layout import basic_layout


required_conan_version = '>=1.53.0'


class USearchConan(ConanFile):
    name = 'usearch'
    license = 'Apache-2.0'
    description = 'Smaller & Faster Single-File Vector Search Engine from Unum'
    homepage = 'https://github.com/unum-cloud/usearch'
    topics = ('search', 'vector', 'simd')
    settings = "os", "arch", "compiler", "build_type"
    url = 'https://github.com/conan-io/conan-center-index'
    package_type = "header-library"

    # No settings/options are necessary, this is header only
    # Potentially add unit-tests in the future:
    # https://docs.conan.io/1/howtos/header_only.html#with-unit-tests
    # no_copy_source = True

    @property
    def _min_cppstd(self):
        return 11

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)


    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(
            self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.hpp",
            dst=os.path.join(self.package_folder, "include/usearch"),
            src=os.path.join(self.source_folder, "include/usearch"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
