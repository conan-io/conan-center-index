from conan import ConanFile
from conan.errors import ConanException
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        self.output.info("Version:")
        self.run("awk --version", env="conanbuild")
        self.run("awk \'BEGIN {print ARGV[1]}\' \"Hello, World\"", env="conanbuild")
