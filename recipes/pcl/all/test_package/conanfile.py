from conans import ConanFile, CMake
import os


class PclTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    short_paths = True

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def imports(self):
        self.copy("*.dll", "bin", "bin")

    def test(self):
        os.chdir('bin')
        self.run('.{}pcl_test_package'.format(os.sep))

