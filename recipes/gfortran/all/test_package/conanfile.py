from conans import ConanFile, tools
import os

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _source(self):
        return os.path.join(self.source_folder, "hello.f90")

    @property
    def _exe(self):
        return os.path.join("bin", "hello")

    def build(self):
        if not tools.cross_building(self):
            self.run("gfortran --version", run_environment=True)
            tools.mkdir("bin")
            self.run("gfortran %s -o %s" % (self._source, self._exe), run_environment=True)

    def test(self):
        if not tools.cross_building(self):
            self.run(self._exe, run_environment=True)
