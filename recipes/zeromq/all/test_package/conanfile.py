from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["WITH_LIBSODIUM"] = self.options["zeromq"].encryption == "libsodium"
        cmake.definitions["ZEROMQ_SHARED"] = self.options["zeromq"].shared
        cmake.definitions["WITH_NORM"] = self.options["zeromq"].with_norm
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
