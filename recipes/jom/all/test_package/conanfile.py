from conans import ConanFile


class TestPackageConan(ConanFile):
    settings = "os"

    def test(self):        
        self.run("jom /VERSION")
