from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            zipFile_path = os.path.abspath(os.path.join(__file__, "..","zipFile.zip"))
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path + " " + zipFile_path, run_environment=True)
