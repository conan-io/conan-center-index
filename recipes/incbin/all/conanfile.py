from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.65.0"

class IncbinConan(ConanFile):
    name = "incbin"
    description = "Include binary files in C/C++"
    license = "Unlicense"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/graphitemaster/incbin/"
    topics = ("include", "binary", "preprocess")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        if self.info.settings.get_safe("compiler") != "msvc":
            self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = CMakeToolchain(self)
            tc.generate()

    def build(self):
        if is_msvc(self):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def package(self):
        copy(self, "UNLICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "incbin.h", dst=os.path.join(self.package_folder, "include"), src=self.source_folder)
        
        if is_msvc(self):
            cmake = CMake(self)
            cmake.install()

    def package_info(self):
        self.cpp_info.libdirs = []
        
        if not is_msvc(self):
            self.cpp_info.bindirs = []
