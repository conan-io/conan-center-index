from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["ROCKSDB_DLL"] = self.options["rocksdb"].shared

        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            if not self.options["rocksdb"].shared:
                bin_path = os.path.join("bin", "test_package_cpp")
                self.run(bin_path, run_environment=True)

            bin_path = os.path.join("bin", "test_package_c")
            self.run(bin_path, run_environment=True)
