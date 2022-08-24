import os
from conan import ConanFile, tools
from conans import CMake


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["MPDECIMAL_CXX"] = self.options["mpdecimal"].cxx
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self.run("{} 13 100".format(os.path.join("bin", "test_package")), run_environment=True)
            if self.options["mpdecimal"].cxx:
                self.run("{} 13 100".format(os.path.join("bin", "test_package_cpp")), run_environment=True)
