from conan import ConanFile
from conan.tools.build import cross_building
from conans import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "pkg_config"

    def build(self):
        self.run("pkg-config --validate ./uuid.pc")
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
