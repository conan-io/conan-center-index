import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.50.0"


class BitFlags(ConanFile):
    name = "bitflags"
    description = "Single-header header-only C++11 / C++14 / C++17 library for easily managing set of auto-generated type-safe flags"
    topics = ("bits", "bitflags", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/m-peko/bitflags"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _minimum_compilers_version(self):
        return {"apple-clang": "5", "clang": "5", "gcc": "7", "Visual Studio": "14"}

    @property
    def _minimum_cpp_standard(self):
        return 11

    def layout(self):
        basic_layout(self)

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)
        try:
            if Version(self.settings.compiler.version) < self._minimum_compilers_version[str(self.settings.compiler)]:
                raise ConanInvalidConfiguration(f"{self.name} requires a compiler that supports C++{self._minimum_cpp_standard}. {self.settings.compiler}, {self.settings.compiler.version}")
        except KeyError:
            self.output.warn("Unknown compiler encountered. Assuming it supports C++11.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True,
            destination=self.source_folder)

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, pattern="*", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_id(self):
        self.info.clear()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "bitflags")
        self.cpp_info.set_property("cmake_target_name", "bitflags::bitflags")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "bitflags"
        self.cpp_info.names["cmake_find_package_multi"] = "bitflags"
