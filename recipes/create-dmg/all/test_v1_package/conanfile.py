from conans import ConanFile
from conan.tools.build import can_run


class TestPackageV1Conan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def test(self):
        if can_run(self):
            self.run("create-dmg --version", run_environment=True)
