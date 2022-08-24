from conan import ConanFile, tools
from conans import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            with tools.run_environment(self):
                cmake = CMake(self)
                cmake.configure()
                cmake.build()

    def test(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            self.run("win_flex --version", run_environment=True)
            self.run("win_bison --version", run_environment=True)

            self.run(os.path.join("bin", "bison_test_package"), run_environment=True)
            self.run("{} {}".format(os.path.join("bin", "flex_test_package"), os.path.join(self.source_folder, "basic_nr.txt")), run_environment=True)
