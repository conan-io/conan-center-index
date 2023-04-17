from conans import ConanFile, CMake, tools
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
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(f"{bin_path} -s", run_environment=True)
            bin_global_path = os.path.join("bin", "test_package_global")
            self.run(f"{bin_global_path} -s", run_environment=True)
