from conan import ConanFile


class TestPackageConan(ConanFile):
    settings = "os", "arch"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        self.run("b2 -v", run_environment=True)
