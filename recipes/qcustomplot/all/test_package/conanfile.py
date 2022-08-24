from conan import ConanFile, tools
from conans import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        with tools.run_environment(self):
            cmake = CMake(self)
            cmake.definitions["QT_VERSION"] = self.deps_cpp_info["qt"].version
            cmake.configure()
            cmake.build()

    def test(self):
        # can't run in Linux agents (headless)
        if not (tools.build.cross_building(self, self) or self.settings.os == "Linux"):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
