from conan import ConanFile
from conan.tools.files import copy
import os

class VStatsConan(ConanFile):
    name = "vstats"
    version = "1.0.0"
    license = "MIT"
    author = "Vansh <vanshbhardwajhere@gmail.com>"
    url = "https://github.com/vanshbhardwajhere/vstats"
    description = "Header-only C++ utility for timing and loop tracking."
    topics = ("timing", "monitoring", "metrics", "header-only", "c++")
    settings = "os", "compiler", "build_type", "arch"
    no_copy_source = True
    exports_sources = "include/*"
    package_type = "header-library"

    def package(self):
        copy(self, "*.hpp", self.source_folder, os.path.join(self.package_folder, "include"))
        copy(self, "*.h", self.source_folder, os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = []
