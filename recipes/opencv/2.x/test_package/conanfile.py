from conans import ConanFile, CMake, tools
import os


class OpenCVTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            peppers = os.path.join(self.source_folder, "peppers.jpg")
            res_path = self.deps_cpp_info["opencv"].res_paths[0]
            self.run("{} {} {}".format(bin_path, res_path, peppers), run_environment=True)
