from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=2.0"

class DotenvConan(ConanFile):
    name = "dotenv"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Ayush272002/dotenv"
    description = "A simple, header-only C++23 dotenv parser"
    topics = ("dotenv", "header-only", "environment", "configuration", "parser")
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
        copy(self, "*.hpp", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
