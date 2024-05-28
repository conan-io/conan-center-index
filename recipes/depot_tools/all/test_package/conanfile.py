from conan import ConanFile
from conan.tools.cmake import cmake_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        # cit: Chrome Infrastructure CLI
        self.run("cit --help")
