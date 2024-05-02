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
            # Test programs consuming shaderc lib
            bin_path_shaderc_c = os.path.join("bin", "test_package_shaderc_c")
            self.run(bin_path_shaderc_c, run_environment=True)
            bin_path_shaderc_cpp = os.path.join("bin", "test_package_shaderc_cpp")
            self.run(bin_path_shaderc_cpp, run_environment=True)

            self.run(f"glslc -h", run_environment=True)
