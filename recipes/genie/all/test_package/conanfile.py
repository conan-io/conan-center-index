from conan import ConanFile, tools


class TestPackageConan(ConanFile):

    settings = "os", "arch"

    def test(self):
        if not tools.build.cross_building(self, self.settings):
            self.run('genie ninja --scripts="{}"'.format(self.source_folder), run_environment=True)
