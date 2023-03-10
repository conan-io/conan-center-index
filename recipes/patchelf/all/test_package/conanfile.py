from conan import ConanFile
from conan.build import cross_building


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        if not cross_building(self, skip_x64_x86=True):
            self.run("patchelf --version")
