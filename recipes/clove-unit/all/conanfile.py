from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"

class CloveUnitConan(ConanFile):
    name = "clove-unit"
    description = "Single-header Unit Testing framework for C (interoperable with C++) with test autodiscovery feature"
    topics = ("unit-testing", "testing", "unit testing", "test")
    homepage = "https://github.com/fdefelici/clove-unit"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    no_copy_source = True
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "clove-unit.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
