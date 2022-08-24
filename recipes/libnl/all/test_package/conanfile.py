import os.path

from conan import ConanFile, tools
from conans import CMake


class NetlinkTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join(self.build_folder, "bin", "show_links")
            self.run(bin_path, cwd=self.source_folder, run_environment=True)
