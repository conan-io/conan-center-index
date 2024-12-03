from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.files import copy, export_conandata_patches, get
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=2.0"


class RustyCppConan(ConanFile):
    name = "rusty-cpp"
    description = "Write C++ code like Rust!"
    # dual licensed under the Apache License v2.0 and the MIT License
    license = "Apache-2.0", "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/seekstar/rusty-cpp"
    topics = ("C++", "Rust", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

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
        copy(self, "LICENSE-APACHE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE-MIT", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_target_name", "rusty-cpp")
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = []
