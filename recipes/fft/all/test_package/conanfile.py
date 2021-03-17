from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            tools.save("data", "2 2 2")
            for binary in ["fftsg2dt", "fftsg3dt", "shrtdctt"]:
                bin_path = os.path.join("bin", binary)
                self.run(bin_path + "< data", run_environment=True)
