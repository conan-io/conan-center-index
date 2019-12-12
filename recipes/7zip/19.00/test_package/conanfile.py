from conans import ConanFile


class TestPackage(ConanFile):
    settings = "os"

    def test(self):
        if self.settings.os == "Windows":
            self.run("7z.exe")
        else:
            self.run("lzma")