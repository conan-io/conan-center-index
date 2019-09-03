from conans import ConanFile


class TestPackage(ConanFile):
    
    def test(self):
        self.run("7z.exe")