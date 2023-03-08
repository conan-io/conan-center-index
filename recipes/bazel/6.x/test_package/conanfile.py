from conan import ConanFile
from conan.tool.build import can_run


class TestPackage(ConanFile):
    settings = "os", "arch"

    def test(self):
        if can_run(self):
          self.run("bazel --version", run_environment=True)
