from conan import ConanFile
from conan.tools.build import can_run

required_conan_version = ">=1.49.0"

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        if can_run(self):
            self.run("genie ninja")
