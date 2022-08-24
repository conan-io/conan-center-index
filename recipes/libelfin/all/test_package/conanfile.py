from conan import ConanFile, tools
from conan.tools.cmake import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if tools.cross_building(self.settings):
            return
        bin_path = os.path.join("bin", "test_package")
        elf_path = os.path.join(self.source_folder, "hello")
        self.run("{} {}".format(bin_path, elf_path), run_environment=True)
