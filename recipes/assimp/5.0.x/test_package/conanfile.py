import os
from conans import ConanFile, CMake, tools


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
            obj_path = os.path.join(self.source_folder, "box.obj")
            bin_c_path = os.path.join("bin", "test_package_c")
            self.run("{0} {1}".format(bin_c_path, obj_path), run_environment=True)
