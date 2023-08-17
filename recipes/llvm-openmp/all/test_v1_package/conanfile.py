from conans import ConanFile, CMake, tools
import os


class LLVMOpenMpTestConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            for executable in ["test_package_cxx", "test_package_c"]:
                bin_path = os.path.join("bin", executable)
                self.run(bin_path, run_environment=True)
