from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["ZINT_WITH_QT"] = self.options["zint"].with_qt
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
            if self.options["zint"].with_qt:
                bin_path = os.path.join("bin", "test_package_cpp")
                self.run(bin_path, run_environment=True)
