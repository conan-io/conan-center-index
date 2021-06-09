import os

from conans import ConanFile, CMake, tools


class LibiglTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            if self.settings.os == "Macos":
                self.run(os.path.join(self.build_folder, "bin", "example"))
            else:
                self.run(os.path.join(self.build_folder, "example"))