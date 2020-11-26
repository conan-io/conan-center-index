from conans import ConanFile, CMake, tools
from conans.errors import ConanException
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    @property
    def _test_shared_library(self):
        try:
            return self.options["libx265"].fPIC
        except ConanException:
            return True

    def build(self):
        cmake = CMake(self)
        cmake.definitions["TEST_LIBRARY"] = self._test_shared_library
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = self.build_folder.replace("\\", "/")
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            with tools.environment_append({"LD_LIBRARY_PATH": "bin", "DYLD_LIBRARY_PATH": "bin"}):
                bin_path = os.path.join("bin", "test_package")
                self.run(bin_path, run_environment=True)
