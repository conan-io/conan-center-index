import os
from conans import ConanFile, CMake, tools


class Box2DTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch", "cppstd"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def imports(self):
        self.copy(pattern="*.dll", src="bin", dst="bin")
        self.copy(pattern="*.dylib", src="lib", dst="bin")

    def test(self):
        bin_path = os.path.join("bin", "test_package")
        self.run(bin_path, run_environment=True)
