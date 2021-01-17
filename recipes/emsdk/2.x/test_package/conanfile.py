from conans import ConanFile, tools

class TestPackgeConan(ConanFile):
    settings = "os", "arch"

    def build(self):
        pass #nothing to do, not warnings please

    def test(self):
        if not tools.cross_building(self):
            compiler = 'em++.bat' if self.settings.os == 'Windows' else './emcc'
            self.run("{} -v".format(compiler), run_environment=True)
