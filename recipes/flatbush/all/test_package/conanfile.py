from conans import ConanFile, CMake, tools
from conans.tools import Version
import os

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.verbose = True
        cmake.configure()
        cmake.build()

    def configure(self):
        compiler = self.settings.compiler

        if compiler.cppstd:
            tools.check_min_cppstd(self, 11)

        if (compiler == "gcc" and Version(compiler.version) < 6) and (compiler == "apple-clang" and compiler.version == "None"):
            compiler.cppstd = "11"

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
