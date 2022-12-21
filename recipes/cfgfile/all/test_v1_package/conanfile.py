from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def build_requirements(self):
        if hasattr(self, "settings_build"):
            self.build_requires(str(self.requires["cfgfile"]))

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            cfg_path = os.path.join(self.source_folder, os.pardir, "test_package", "test.cfg")
            self.run("{} \"{}\"".format(bin_path, cfg_path), run_environment=True)
