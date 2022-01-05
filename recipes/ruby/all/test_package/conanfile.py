from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.gnu import PkgConfigDeps
from conans import tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def generate(self):
        pc = PkgConfigDeps(self)
        pkgconfig_dir = os.path.join('lib', 'pkgconfig')
        tools.mkdir(pkgconfig_dir)
        with tools.chdir(pkgconfig_dir):
            pc.generate()

        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        self.run("ruby --version", run_environment=True)

        if not tools.cross_building(self.settings):
            CMake(self).test(output_on_failure=True)
