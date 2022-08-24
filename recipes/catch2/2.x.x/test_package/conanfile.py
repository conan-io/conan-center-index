from conan import ConanFile, tools
from conans import CMake
from conan.tools.scm import Version
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["WITH_MAIN"] = self.options["catch2"].with_main
        cmake.definitions["WITH_BENCHMARK"] = self.options["catch2"].with_main and self.options["catch2"].with_benchmark
        cmake.definitions["WITH_PREFIX"] = self.options["catch2"].with_prefix
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self.settings):
            self.run(os.path.join("bin", "test_package"), run_environment=True)
            if self.options["catch2"].with_main:
                self.run(os.path.join("bin", "standalone"), run_environment=True)
                if self.options["catch2"].with_benchmark:
                    self.run(os.path.join("bin", "benchmark"), run_environment=True)
