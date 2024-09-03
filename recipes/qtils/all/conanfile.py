import os
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy,get

required_conan_version = ">=2.0.5"

class PackageConan(ConanFile):
    name = "qtils"
    version = "0.0.4"
    description = "Utils for KAGOME C++ projects"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/qdrvm/qtils"
    topics = ("KAGOME")
    package_type = "header-library"
    settings = "os", "compiler", "build_type", "arch"

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        # Only header files, no source files that need to be compiled, so skip the build step
        pass

    def package(self):
        include_folder = os.path.join(self.source_folder, "src")
        copy(self, "*.hpp", dst=os.path.join(self.package_folder, "include"), src=include_folder, keep_path=True)

    def package_info(self):
        # Only header files, no library files need to be linked
        self.cpp_info.libdirs = []
        self.cpp_info.libs = []
        self.cpp_info.includedirs = ["include"]
