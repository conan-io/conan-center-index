from conan import ConanFile
from conan.tools.cmake import cmake_layout
from conan.tools.files import copy, get
import os

required_conan_version = ">=1.33.0"

class ShieldConan(ConanFile):
    name = "shield"
    topics = ("utility", "warnings", "suppression")
    description = "C++ warning suppression headers."
    settings = "os", "compiler", "build_type", "arch"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/holoplot/shield"
    license = "MIT"
    no_copy_source = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder,"licenses"), src=self.source_folder)
        copy(self, pattern="*", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))

    def package_id(self):
        self.info.clear()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "shield"
        self.cpp_info.names["cmake_find_package_multi"] = "shield"
