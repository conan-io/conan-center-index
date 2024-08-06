import os

from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.build import can_run


class reflect_cppTestConan(ConanFile):
    settings = {
        "os": ["Linux", "Windows", "Macos"],
        "compiler": {
            "gcc": {"cppstd": [20]},
            "msvc": {"cppstd": [20]},
            "clang": {"cppstd": [20]},
        },
        "arch": None,
        "build_type": None,
    }
    generators = "CMakeDeps", "CMakeToolchain"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def layout(self):
        cmake_layout(self)

    def test(self):
        if can_run(self):
            cmd = os.path.join(self.cpp.build.bindir, "reflectcpp-test")
            self.run(cmd, env="conanrun")

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "17",
            "msvc": "193",
            "gcc": "11.4",
            "clang": "16",
            "apple-clang": "15",
        }
