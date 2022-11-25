from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["SFML_WITH_WINDOW"] = self.options["sfml"].window
        cmake.definitions["SFML_WITH_GRAPHICS"] = self.options["sfml"].graphics
        cmake.definitions["SFML_WITH_NETWORK"] = self.options["sfml"].network
        cmake.definitions["SFML_WITH_AUDIO"] = self.options["sfml"].audio
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
