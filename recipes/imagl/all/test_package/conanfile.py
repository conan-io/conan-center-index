import os
from conans import ConanFile, CMake, tools


class ImaglTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        generator = "Ninja" if str(self.settings.compiler) == "Visual Studio" else None
        cmake = CMake(self, generator=generator)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "example")
            self.run(bin_path, run_environment=True)
