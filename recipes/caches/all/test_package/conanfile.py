from conan import ConanFile
from conan.tools.scons import SConsDeps


class TestPackageConan(ConanFile):
    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.test_requires("gtest/1.12.1")

    def generate(self):
        SConsDeps(self).generate()

    def test(self):
        self.run("scons test")
