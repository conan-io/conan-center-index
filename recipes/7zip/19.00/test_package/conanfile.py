from conans import ConanFile, tools


class TestPackageConan(ConanFile):
    # Add comment
    settings = "os", "arch", "compiler", "build_type"

    def test(self):
        if not tools.cross_building(self):
            self.run("7z.exe")
