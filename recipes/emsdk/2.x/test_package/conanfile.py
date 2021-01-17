from conans import ConanFile, tools, CMake

class TestPackgeConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def build(self):
        # To use the build-helper we need a cross-building scenario
        self.run('emcmake cmake "{}"'.format(self.source_folder), run_environment=True)
        self.run('emmake make', run_environment=True)

    def test(self):
        if not tools.cross_building(self):
            self.run('node test_package.js', run_environment=True)
            compiler = 'em++.bat' if self.settings.os == 'Windows' else 'emcc'
            self.run("{} -v".format(compiler), run_environment=True)
