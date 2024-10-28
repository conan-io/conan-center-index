from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"

class EmbeddedTemplateLibraryConan(ConanFile):
    name = "etl"
    description = "A C++ template library for embedded applications"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.etlcpp.com/"
    topics = ("cpp", "embedded", "template", "container", "utility", "framework", "messaging", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "etl")
        self.cpp_info.set_property("cmake_target_name", "etl::etl")
        self.cpp_info.set_property("cmake_target_aliases", ["etl"]) # legacy target before 20.27.2

        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
