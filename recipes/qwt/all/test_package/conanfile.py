from conans import ConanFile, CMake, tools
import os


class QwtTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "example")
            self.run(bin_path, run_environment=True)
