from conan import ConanFile


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def build_requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        self.run("bear --version", env="conanrun")
