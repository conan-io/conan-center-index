import os

from conans import ConanFile, CMake, tools


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        packio_version = self.deps_cpp_info["packio"].version
        cmake = CMake(self)
        cmake.configure(defs={"PACKIO_VERSION": packio_version})
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            self.run(os.path.join("bin", "main"), run_environment=True)
