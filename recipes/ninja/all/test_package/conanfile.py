from conan import ConanFile


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def build_requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        self.run("ninja --version", env="conanrun")
