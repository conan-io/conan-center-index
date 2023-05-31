from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.53.0"

class TurtleConan(ConanFile):
    name = "turtle"
    description = "Turtle is a C++ mock object library based on Boost with a focus on usability, simplicity and flexibility."
    topics = ("mock", "test", "boost")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mat007/turtle"
    license = "BSL-1.0"
    no_copy_source = True
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        basic_layout(self, src_folder="include/turtle")

    def requirements(self):
        self.requires("boost/1.81.0")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE_1_0.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "*.hpp", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))
