from conans import ConanFile


class TestPackageConan(ConanFile):
    def test(self):
        # cit: Chrome Infrastructure CLI
        self.run("cit --help", run_environment=True)
