from conans import ConanFile, CMake, tools
import os


class MimallocTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings, skip_x64_x86=True):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)

            test_package_cpp = os.path.join("bin", "test_package_cpp")
            self.run(test_package_cpp, run_environment=True)
