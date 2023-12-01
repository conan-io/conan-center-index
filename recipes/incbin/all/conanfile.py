from conan import ConanFile
from conans import CMake
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.50.0"


class IncbinConan(ConanFile):
    name = "incbin"
    description = "Include binary files in C/C++"
    license = "Unlicense"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/graphitemaster/incbin/"
    topics = ("include", "binary", "preprocess", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        if is_msvc(self):
            with open("CMakeLists.txt", "w") as f:
                f.write("cmake_minimum_required(VERSION 3.0)\n"
                        "project(incbin_tool)\n"
                        "add_executable(incbin_tool incbin.c)\n")

    def build(self):
        if is_msvc(self):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def package(self):
        copy(self, "UNLICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "incbin.h", dst=os.path.join(self.package_folder, "include"), src=self.source_folder)
        copy(self, "incbin_tool.exe", dst=os.path.join(self.package_folder, "bin"), src=self.build_folder, keep_path=False)

    def package_id(self):
        if not is_msvc(self):
            self.info.clear()

    def package_info(self):
        self.cpp_info.libdirs = []
        if is_msvc(self):
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        else:
            self.cpp_info.bindirs = []
