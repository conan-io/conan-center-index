from conans import ConanFile, CMake, tools
from conans.errors import ConanException
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        if self.options["magnum-extras"].ui:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self):
            if self.options["magnum-extras"].player:
                self.run("magnum-player --help")
            if self.options["magnum-extras"].ui_gallery:
                self.run("magnum-ui-gallery --help")
            if self.options["magnum-extras"].ui:
                bin_path = os.path.join("bin", "test_package")
                self.run(bin_path, run_environment=True)
