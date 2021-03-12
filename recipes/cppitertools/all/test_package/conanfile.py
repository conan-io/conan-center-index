import os
from conans import ConanFile, CMake, tools


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        if self.options["cppitertools"].zip_longest:
            cmake.definitions["ZIP_LONGEST"] = True
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)

            if self.options["cppitertools"].zip_longest:
                bin_path = os.path.join("bin", "test_zip_longest")
                self.run(bin_path, run_environment=True)
