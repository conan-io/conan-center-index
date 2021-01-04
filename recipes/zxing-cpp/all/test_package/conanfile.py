from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def requirements(self):
        self.requires("stb/20200203")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            try:
                os.unlink("output.png")
            except FileNotFoundError:
                pass
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)

            assert os.path.isfile("output.png")
