from conans import ConanFile, tools


class TestPackageConan(ConanFile):

    settings = "os", "arch"

    def test(self):
        if not tools.cross_building(self.settings):
            self.run('genie ninja --scripts="{}"'.format(self.source_folder), run_environment=True)
