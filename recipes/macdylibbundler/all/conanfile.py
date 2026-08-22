from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.files import copy, get
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.errors import ConanInvalidConfiguration

import os

required_conan_version = ">=1.53.0"


class MacDylibBundlerConan(ConanFile):
    name = "macdylibbundler"
    package_type = "application"
    description = (
        "mac dylib bundler is a tool for use when bundling mac applications"
    )
    topics = ("build", "dylib", "installer", "mac")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/auriamg/macdylibbundler"
    license = "MIT"
    settings = "os", "arch", "build_type"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if not is_apple_os(self):
            raise ConanInvalidConfiguration("This tool is for macOS only")

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
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        # The CMakeLists.txt misses the install command, so for simplicity the executable is copied manually
        copy(self, "dylibbundler", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
