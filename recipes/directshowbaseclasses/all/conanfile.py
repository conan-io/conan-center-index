import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get

required_conan_version = ">=1.53.0"


class DirectShowBaseClassesConan(ConanFile):
    name = "directshowbaseclasses"
    description = (
        "Microsoft DirectShow Base Classes are a set of C++ classes and "
        "utility functions designed for implementing DirectShow filters"
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://docs.microsoft.com/en-us/windows/desktop/directshow/directshow-base-classes"
    topics = ("directshow", "dshow")

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    short_paths = True

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} can only be used on Windows.")
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=self.source_path.parent)
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["strmbasd" if self.settings.build_type == "Debug" else "strmbase"]
        self.cpp_info.system_libs = ["strmiids", "winmm"]
