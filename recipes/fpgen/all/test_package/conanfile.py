import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def configure(self):
        v = int(str(self.settings.compiler.version).split(",")[0])
        if self.settings.compiler == "gcc" and v < 10:
            raise ConanInvalidConfiguration("Requires GCC > 10")
        elif not self.settings.compiler == "gcc":
            raise ConanInvalidConfiguration("Currently only GCC supported")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
