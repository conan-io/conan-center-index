from conan import ConanFile

required_conan_version = ">=1.52.0"


class TestPackageConan(ConanFile):
    settings = "os", "arch"

    def test(self):
        self.run("b2 -v", run_environment=True)
