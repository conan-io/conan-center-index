from conan import ConanFile, tools$


class TestPackage(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    
    def test(self):
        if not tools.build.cross_building(self, self):
            self.run("perf version")
