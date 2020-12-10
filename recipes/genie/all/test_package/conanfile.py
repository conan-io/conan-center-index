from conans import ConanFile, tools


class TestPackageConan(ConanFile):

    settings = "arch_build", "os_build"

    def test(self):
        bin_ext = ".exe" if self.settings.os_build == "Windows" else ""
        print(self.build_folder)
        if not tools.cross_building(self.settings):
            self.run("genie{} ninja --scripts={}".format(bin_ext, self.source_folder))
