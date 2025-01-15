from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.65.0"

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

    def configure(self):
        self._is_msvc = is_msvc(self)

    def package_id(self):
        if self._is_msvc:
            self.info.settings.rm_safe("compiler.libcxx")
            self.info.settings.rm_safe("compiler.cppstd")
        else:
            self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        if self._is_msvc:
            with open("CMakeLists.txt", "w") as f:
                f.write("cmake_minimum_required(VERSION 3.0)\n"
                        "project(incbin_tool)\n"
                        "add_executable(incbin_tool incbin.c)\n"
                        "install(TARGETS incbin_tool)")

    def build(self):
        if self._is_msvc:
            tc = CMakeToolchain(self)
            tc.generate()
            cmake = CMake(self)
            cmake.configure()
            cmake.build()
            cmake.install()

    def package(self):
        copy(self, "UNLICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "incbin.h", dst=os.path.join(self.package_folder, "include"), src=self.source_folder)
        copy(self, "incbin_tool.exe", dst=os.path.join(self.package_folder, "bin"), src=self.build_folder, keep_path=False)

    def package_info(self):
        self.cpp_info.libdirs = []
        if self._is_msvc:
            self.buildenv_info.append("PATH", os.path.join(self.package_folder, "bin"))
        else:
            self.cpp_info.bindirs = []
