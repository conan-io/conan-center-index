import os

from conan import ConanFile
from conan.tools.layout import basic_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        basic_layout(self)

    def build(self):
        src = os.path.join(self.source_folder, "test_package.c")
        self.run(f"makedepend -f- -- -- {src}")

    def test(self):
        pass
