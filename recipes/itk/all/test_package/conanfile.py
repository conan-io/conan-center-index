from conans import ConanFile, CMake, tools
import os


class HelloTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    version = "4.13.2"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def requirements(self):
        self.requires("itk/{0}".format(self.version))

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "example")
            self.run(bin_path, run_environment=True)
