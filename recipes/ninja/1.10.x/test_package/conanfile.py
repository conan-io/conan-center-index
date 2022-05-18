from conans import ConanFile


class TestPackage(ConanFile):

    def build(self):
        pass

    def test(self):
        self.run("ninja --version", run_environment=True)
