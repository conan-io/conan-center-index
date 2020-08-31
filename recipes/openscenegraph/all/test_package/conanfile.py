from conans import ConanFile, CMake, CMakeToolchain, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_find_package"

    def toolchain(self):
        to_int = lambda x: 1 if x else 0
        toolchain = CMakeToolchain(self)
        toolchain.definitions["WITH_PNG"] = to_int(self.settings.os == "Macos" or self.options["openscenegraph"].with_png)
        toolchain.definitions["WITH_DCMTK"] = to_int(self.options["openscenegraph"].with_dcmtk)
        toolchain.write_toolchain_files()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join(os.curdir, "test_package") + (".exe" if self.settings.os == "Windows" else "")
            self.run(bin_path, run_environment=True)
