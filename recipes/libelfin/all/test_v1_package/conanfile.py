from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if tools.cross_building(self.settings):
            return
        bin_path = os.path.join("bin", "test_package")
        elf_path = os.path.join(self.source_folder, os.pardir, "test_package", "hello")
        self.run(f"{bin_path} {elf_path}", run_environment=True)
