import os

from conans import CMake, ConanFile, tools


class RabbitmqcTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["WITH_SSL"] = self.options["rabbitmq-c"].ssl
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "PackageTest")
            self.run(bin_path, run_environment=True)
