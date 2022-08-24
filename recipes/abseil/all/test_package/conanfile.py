from conan import ConanFile, tools
from conans import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["CXX20_SUPPORTED"] = tools.Version(self.deps_cpp_info["abseil"].version) > "20210324.2"
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self):
            bin_path = os.path.join("bin", "test_package")
            self.run("%s -s" % bin_path, run_environment=True)
            bin_global_path = os.path.join("bin", "test_package_global")
            self.run("%s -s" % bin_global_path, run_environment=True)
