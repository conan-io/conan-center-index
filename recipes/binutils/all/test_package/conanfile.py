from conans import ConanFile, tools

class TestPackageConan(ConanFile):

    settings = "os"

    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        self.run("as --version")
