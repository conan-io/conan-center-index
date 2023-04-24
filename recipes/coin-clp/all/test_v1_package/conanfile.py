from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "pkg_config"

    def build_requirements(self):
        self.build_requires("pkgconf/1.9.3")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            mps = os.path.join(self.source_folder, os.pardir, "test_package", "sample.mps")
            self.run(f"{bin_path} {mps}", run_environment=True)
