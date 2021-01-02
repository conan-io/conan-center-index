from conans import ConanFile, tools

class TestPackgeConan(ConanFile):
    settings = "os", "arch"

    def build(self):
        pass #nothing to do, not warnings please

    def test(self):
        if not tools.cross_building(self):
            if self.settings.os == "Windows":
                self.run("ndk-build.cmd --version", run_environment=True)
            else:
                self.run("ndk-build --version", run_environment=True)
