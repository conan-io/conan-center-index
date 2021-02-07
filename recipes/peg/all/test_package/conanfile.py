from conans import ConanFile

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def test(self):
        if not self.settings.os == "Windows":
            self.run("peg -V")
