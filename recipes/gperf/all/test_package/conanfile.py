from conans import ConanFile, tools


class TestPackageConan(ConanFile):
    settings = "os", "arch"
    test_type = "build_requires"

    def test(self):
        if not tools.cross_building(self):
            self.run("gperf --version")
