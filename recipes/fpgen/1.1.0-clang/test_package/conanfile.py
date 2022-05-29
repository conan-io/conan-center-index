import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        if self.settings.compiler == "clang":
            self.settings.compiler.libcxx = "libc++"
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
