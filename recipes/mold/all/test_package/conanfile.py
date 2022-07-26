import os
from conans import ConanFile, tools
from conan.tools.build import cross_building

class TestPackageConan(ConanFile):
    settings = "os", "arch", "build_type", "compiler"

    def test(self):
        if not cross_building(self):
            self.run("mold -v", run_environment=True)
