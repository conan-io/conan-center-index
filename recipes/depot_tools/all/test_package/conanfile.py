from conans import ConanFile


class TestPackageConan(ConanFile):
    def test(self):
        self.run("ninja --version", run_environment=True)
