from conan import ConanFile
from conan.tools.build import cross_building


class TestPackageConan(ConanFile):

    settings = "os", "arch"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        if not cross_building(self):
            self.output.info("Node version:")
            self.run("node --version")
