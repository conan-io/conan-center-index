from conans import ConanFile, CMake, tools
from conans.tools import Version
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    _with_main = False
    _with_benchmark = False

    def build(self):
        self._with_main = self.options["catch2"].with_main if "with_main" in self.options["catch2"].keys() else True
        self._with_benchmark = self.options["catch2"].with_benchmark if "with_benchmark" in self.options["catch2"].keys() else False

        cmake = CMake(self)
        cmake.definitions["WITH_MAIN"] = self._with_main
        cmake.definitions["WITH_BENCHMARK"] = self._with_main and self._with_benchmark
        cmake.definitions["WITH_PREFIX"] = self.options["catch2"].with_prefix
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            if tools.Version(self.deps_cpp_info["catch2"].version) < "3.0.0":
                self.run(os.path.join("bin", "test_package"), run_environment=True)
            if self._with_main:
                self.run(os.path.join("bin", "standalone"), run_environment=True)
                if self._with_benchmark:
                    self.run(os.path.join("bin", "benchmark"), run_environment=True)
