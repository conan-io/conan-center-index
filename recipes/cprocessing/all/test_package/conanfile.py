from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        test_file = os.path.join("bin", "test_package")
        if self.settings.os == "Windows":
            test_file += ".exe"
        assert os.path.exists(test_file)
