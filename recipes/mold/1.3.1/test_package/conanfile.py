from conan import ConanFile
from conan.tools.build import cross_building

class TestPackageConan(ConanFile):
    settings = "os", "arch", "build_type", "compiler"

    def test(self):
        if not cross_building(self):
            self.run("mold -v", run_environment=True)
