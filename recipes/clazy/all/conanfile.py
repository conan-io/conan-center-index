import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir

required_conan_version = ">=2.1"


class ClazyConan(ConanFile):
    name = "clazy"
    description = "Code beautifier"
    license = "GPL-2.0-or-later"
    topics = "beautifier", "command-line"
    homepage = "https://github.com/KDE/clazy"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler

    def validate(self):
        if not str(self.settings.compiler).endswith("clang"):
            raise ConanInvalidConfiguration(f"{self.ref} support only clang compiler")

    def build_requirements(self):
        self.tool_requires("llvm-core/13.0.0")

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
        copy(self, "COPYING-LGPL2.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
