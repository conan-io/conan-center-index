from conans import ConanFile
from conan.tools.build import can_run


class TestPackageV1Conan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def build(self):
        pass

    def test(self):
        if can_run(self):
            self.run("jom /VERSION", run_environment=True)
