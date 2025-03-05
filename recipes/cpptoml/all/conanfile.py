import os

from conan import ConanFile
from conan.tools.files import copy, get, export_conandata_patches, apply_conandata_patches
from conan.tools.layout import basic_layout

required_conan_version = ">=1.50.0"


class CppTomlConan(ConanFile):
    name = "cpptoml"
    description = "cpptoml is a header-only library for parsing TOML "
    topics = ("toml", "header-only", "configuration")
    license = "MIT"
    homepage = "https://github.com/skystrife/cpptoml"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "cpptoml")
        self.cpp_info.set_property("cmake_target_name", "cpptoml")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
