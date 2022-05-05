from conans import ConanFile, tools

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def build(self):
        if not tools.cross_building(self):
            self.run("gfortran --version", run_environment=True)
            self.run("gfortran hello.f90 -o hello%s" % (".exe" if self.settings.os == "Windows" else ""), run_environment=True)

    def test(self):
        if not tools.cross_building(self):
            self.run("hello%s" % (".exe" if self.settings.os == "Windows" else ""), run_environment=True)
