from conans import ConanFile


class TestPackageConan(ConanFile):
    def test(self):
        self.run("gclient --version", run_environment=True)
