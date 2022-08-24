from conan import ConanFile, tools
from conans import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self, build_type="RelWithDebInfo") # To work properly Coz tool requires debug information https://github.com/plasma-umass/coz
        cmake.configure()
        cmake.build()

    def test(self):
        if tools.cross_building(self.settings):
            return
        bin_path = os.path.join("bin", "test_package")
        self.run("coz run --- " + bin_path, run_environment=True)
        print(open("profile.coz").read())
