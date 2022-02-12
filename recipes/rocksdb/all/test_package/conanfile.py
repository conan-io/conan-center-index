from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["ROCKSDB_SHARED"] = self.options["rocksdb"].shared
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            if not self.options["rocksdb"].shared:
                bin_path = os.path.join("bin", "test_package_cpp")
                self.run(bin_path, run_environment=True)

            bin_path = os.path.join("bin", "test_package_stable_abi")
            self.run(bin_path, run_environment=True)
