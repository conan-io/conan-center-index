
import os
from conans.model.conan_file import ConanFile
from conans import CMake, tools


class TestPackageConan(ConanFile):
    name = "pkgtest_embree3"
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        os.chdir("bin")
        self.run(".{0}{1}".format(os.sep, self.name), run_environment=True)
