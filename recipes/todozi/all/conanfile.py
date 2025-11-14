from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
from conan.tools.files import copy, get
from conan.tools.layout import cmake_layout
import os

required_conan_version = ">=1.52.0"

class TodoziConan(ConanFile):
    name = "todozi"
    version = "0.1.0"
    description = "A comprehensive task management system written in C"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cyber-boost/todozi"
    topics = ("task-management", "productivity", "c", "library")
    package_type = "static-library"

    settings = "os", "compiler", "build_type", "arch"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("jansson/[>=2.14 <3]")
        self.requires("libcurl/[>=8.4.0 <9]")
        self.requires("openssl/[>=3.2.0 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="tdz_c")
        cmake.build()

    def package(self):
        # Copy headers
        copy(self, "*.h", os.path.join(self.source_folder, "tdz_c", "include"), os.path.join(self.package_folder, "include"))

        # Copy libraries
        copy(self, "*.a", self.build_folder, os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.lib", self.build_folder, os.path.join(self.package_folder, "lib"), keep_path=False)

        # Copy executables if built
        copy(self, "todozi", self.build_folder, os.path.join(self.package_folder, "bin"), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["todozi"]
