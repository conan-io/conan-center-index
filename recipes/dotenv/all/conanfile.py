from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.scm import Version
import os

required_conan_version = ">=2.0"

class DotenvConan(ConanFile):
    name = "dotenv"
    version = "1.0.0"
    license = "MIT"
    url = "https://github.com/Ayush272002/dotenv"
    homepage = "https://github.com/Ayush272002/dotenv"
    description = "A simple, header-only C++23 dotenv parser"
    topics = ("dotenv", "header-only", "environment", "configuration", "parser")
    package_type = "header-library"
    
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        self.folders.source = "."
        self.folders.build = "build"

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "*.hpp", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = []
