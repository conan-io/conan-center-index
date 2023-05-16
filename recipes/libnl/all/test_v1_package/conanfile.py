import os.path

from conans import ConanFile, CMake, tools


class NetlinkTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join(self.build_folder, "bin", "test_package")
            self.run(bin_path, cwd=self.source_folder, run_environment=True)
