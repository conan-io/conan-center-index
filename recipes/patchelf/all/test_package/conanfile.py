from conan import ConanFile, tools
from conans import CMake


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def test(self):
        if not tools.build.cross_building(self, self, skip_x64_x86=True):
            self.run("patchelf --version", run_environment=True)
