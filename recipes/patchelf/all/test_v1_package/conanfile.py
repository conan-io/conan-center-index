from conans import ConanFile
from conan.tools.build import cross_building


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def test(self):
        if not cross_building(self, skip_x64_x86=True):
            self.run("patchelf --version", run_environment=True)
