import os
from conan import ConanFile


class MinGWTestConan(ConanFile):
    generators = "VirtualBuildEnv"
    settings = "os", "arch"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        self.run("gcc.exe --version")
