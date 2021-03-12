import os

from conans import ConanFile, CMake, tools

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["WITH_EXTENSIONS"] = self.options["cpputest"].with_extensions
        cmake.configure()
        cmake.build()

    def test(self):
        if tools.cross_building(self.settings):
            return

        self.run(os.path.join("bin", "test_package"), run_environment=True)

        if self.options["cpputest"].with_extensions:
            self.run(os.path.join("bin", "test_package_with_extensions"), run_environment=True)
