from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package", "pkg_config"

    def build(self):
        if self.settings.os != 'Windows':
            self.run('g-ir-annotation-tool --version', run_environment=True)
            self.run('g-ir-compiler --version', run_environment=True)
            self.run('g-ir-generate --version', run_environment=True)
            self.run('g-ir-inspect -h', run_environment=True)
            self.run('g-ir-scanner --version', run_environment=True)

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)

