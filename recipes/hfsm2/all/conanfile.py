import os

from conan import ConanFile
from conan.tools.files import copy
from conan.tools.build import check_min_cppstd
from conan.tools.files import get
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import rmdir

required_conan_version = ">=2.0"

class Hfsm2Conan(ConanFile):
    name = "hfsm2"
    description = "High-Performance Hierarchical Finite State Machine Framework"
    license = "MIT"
    topics = ("embedded", "fsm", "state-machine", "cpp", "modern-cpp", "game-development",
              "cpp11", "embedded-systems", "template-metaprogramming", "header-only",
              "mit-license", "fsm-library", "hierarchical-state-machine", "game-dev", "hfsm")
    homepage = "https://hfsm.dev/"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def package_id(self):
        self.info.clear()

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.configure()
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
