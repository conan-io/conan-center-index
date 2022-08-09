from conans import ConanFile, CMake
from conan import tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["ONEDPL_VERSION_MAJOR"] = tools.scm.Version(self.deps_cpp_info["onedpl"].version).major()[0:4]
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
