from conan import ConanFile, tools


class LibsassTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def test(self):
        if not tools.build.cross_building(self, self):
            self.run("sassc --version", run_environment=True)
