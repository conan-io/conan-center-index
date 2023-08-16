from conan import ConanFile
from conan.tools.build import can_run


# legacy validation with Conan 1.x
class TestPackageV1Conan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def test(self):
        if can_run(self):
            self.run("bear --version", run_environment=True)
