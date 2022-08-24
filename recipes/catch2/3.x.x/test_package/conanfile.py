from conan import ConanFile, tools
from conans import CMake
from conans.tools import Version
import os

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["WITH_PREFIX"] = self.options["catch2"].with_prefix
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self):
            self.run(os.path.join("bin", "standalone"), run_environment=True)
            self.run(os.path.join("bin", "benchmark"), run_environment=True)
