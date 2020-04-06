from conans import ConanFile, tools


class TestPackageConan(ConanFile):

    settings = "arch_build", "os_build"

    def test(self):
        bin_ext = ".exe" if self.settings.os_build == "Windows" else ""
        if not tools.cross_building(self.settings):
            self.run("gperf{} --version".format(bin_ext))
