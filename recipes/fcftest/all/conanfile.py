from conan import ConanFile
from conan.tools.files import copy, get
import os

class FcfTestConan(ConanFile):
    name = "fcftest"
    description = "Lightweight header-only cpp unit testing framework"
    license = "MIT"
    url = "https://github.com/fcf-framework/conan-center-index"
    homepage = "https://github.com/fcf-framework/fcfTest"
    topics = ("cpp", "header-only", "testing", "unit-testing", "tdd")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    def source(self):
        get(self, f"https://github.com/fcf-framework/fcfTest/archive/refs/tags/v{self.version}.zip", strip_root=True)

    def package(self):
        copy(self, "test.hpp", src=self.source_folder, dst=os.path.join(self.package_folder, "include", "fcfTest"))
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "fcfTest")
        self.cpp_info.set_property("cmake_target_name", "fcfTest::fcfTest")

