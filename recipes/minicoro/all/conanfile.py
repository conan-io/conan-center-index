from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=1.52.0"


class PackageConan(ConanFile):
    name = "minicoro"
    description = "Single header stackful cross-platform coroutine library in pure C"
    license = ("Unlicense", "MIT-0")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/edubart/minicoro"
    topics = ("lua", "coroutine", "fibers", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", self.source_folder, os.path.join(self.package_folder, "include", "minicoro"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs.append(os.path.join("include", "minicoro"))
