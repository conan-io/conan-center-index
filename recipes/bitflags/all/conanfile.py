from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
import os

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

    def layout(self):
        basic_layout(self)

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
