from conan import ConanFile


class TestPackageConan(ConanFile):
    settings = "os", "arch"

    def test(self):
        self.run("b2 -v", run_environment=True)
