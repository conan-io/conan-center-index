from conan import ConanFile, tools$


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def test(self):
        if not tools.build.cross_building(self, self):
            self.run("create-dmg --version", run_environment=True)
