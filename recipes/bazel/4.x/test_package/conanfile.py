from conans import ConanFile


class TestPackage(ConanFile):
    settings = "os", "arch"

    def test(self):
        self.run("bazel --version", run_environment=True)

