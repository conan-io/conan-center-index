from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            arg_path = bin_path
            if self.settings.os == "Windows":
                arg_path += ".exe"
            self.run("{0} {1}".format(bin_path, arg_path), run_environment=True)
