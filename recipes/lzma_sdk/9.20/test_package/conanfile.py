from conans import ConanFile


class TestPackage(ConanFile):

    def test(self):
        self.run("7zDec")
        self.run("lzma")
