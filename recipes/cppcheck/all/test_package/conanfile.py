from conans import ConanFile


class TestPackageConan(ConanFile):

    def test(self):
        self.run("cppcheck --version", run_environment=True)
