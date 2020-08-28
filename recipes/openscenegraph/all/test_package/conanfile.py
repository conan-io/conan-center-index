from conans import ConanFile, CMake, CMakeToolchain, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_find_package"

    def toolchain(self):
        toolchain = CMakeToolchain(self)
        toolchain.definitions["WITH_PNG"] = 1 if self.options["openscenegraph"].with_png else 0
        toolchain.write_toolchain_files()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join(os.curdir, "test_package")
            self.run(bin_path, run_environment=True)
