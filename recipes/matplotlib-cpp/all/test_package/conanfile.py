from conans import ConanFile, CMake, tools
import os


def import_numpy():
    try:
        import numpy
    except ImportError:
        import pip

        if hasattr(pip, "main"):
            pip.main(["install", "numpy"])
        else:
            pip._internal.main(["install", "numpy"])

        import numpy


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        import_numpy()

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
