from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        if self.settings.arch in ["x86", "x86_64"]:
            arch_defs = {"USE_X86": 1}
        if self.settings.arch in ["armv8", "armv8_32", "armv8.3"]:
            arch_defs = {"USE_AARCH64": 1}
        cmake.configure(defs=arch_defs)
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
