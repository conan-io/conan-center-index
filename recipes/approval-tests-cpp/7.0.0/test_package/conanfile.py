import os
from conans import ConanFile, CMake, tools


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake", "pkg_config"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if tools.cross_building(self.settings):
            self.output.warn("Skipping run cross built package")
            return

        bin_path = os.path.join("bin", "test_package")
        self.run("%s" % bin_path, run_environment=True)
