from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            res_dir = os.path.join(self.source_folder, os.pardir, "test_package")
            obj_path = os.path.join(res_dir, "cube.obj")
            mtl_dir = os.path.join(res_dir, "")
            self.run(f"{bin_path} {obj_path} {mtl_dir}", run_environment=True)
