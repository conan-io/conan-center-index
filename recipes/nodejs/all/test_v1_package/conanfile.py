import os

from conan import ConanFile
from conans.errors import ConanException


class TestPackageConan(ConanFile):

    settings = "os", "arch"
    test_type = "explicit"

    def build_requirements(self):
        self.build_requires(self.tested_reference_str)

    def test(self):
        binary_name = "node.exe" if self.settings.os == "Windows" else "node"
        if not os.path.isfile(os.path.join(self.dependencies[self.tested_reference_str].cpp_info.bindir, binary_name)):
            raise ConanException("node not found in package")
