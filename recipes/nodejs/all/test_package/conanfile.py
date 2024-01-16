import os

from conan import ConanFile
from conan.tools.cmake import cmake_layout
from conans.errors import ConanException


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        if not os.path.isfile(self.dependencies[self.tested_reference_str].cpp_info.bindir):
            raise ConanException("node not found in package")
