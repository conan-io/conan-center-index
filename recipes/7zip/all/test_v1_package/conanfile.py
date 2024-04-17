from conans import ConanFile
from conan.tools.build import can_run


class TestPackageV1Conan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def test(self):
        if can_run(self):
            self.run("7z.exe", run_environment=True)
