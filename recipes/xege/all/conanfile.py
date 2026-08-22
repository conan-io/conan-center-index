import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get

required_conan_version = ">=1.53.0"


class XegeConan(ConanFile):
    name = "xege"
    description = "Easy Graphics Engine, a lite graphics library in Windows"
    license = "LGPLv2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://xege.org/"
    topics = ("ege", "graphics", "gui")

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("This library is only compatible with Windows")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        copy(self, "*.h",
             dst=os.path.join(self.package_folder, "include"),
             src=os.path.join(self.source_folder, "src"))
        for pattern in ["*.lib", "*.a"]:
            copy(self, pattern,
                 dst=os.path.join(self.package_folder, "lib"),
                 src=self.build_folder,
                 keep_path=False)

    def package_info(self):
        if self.settings.arch == "x86_64":
            self.cpp_info.libs = ["graphics64"]
        else:
            self.cpp_info.libs = ["graphics"]
        self.cpp_info.system_libs = ["gdiplus", "uuid", "msimg32", "gdi32", "imm32", "ole32", "oleaut32"]
