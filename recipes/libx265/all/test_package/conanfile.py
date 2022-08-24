from conan import ConanFile, tools
from conans import CMake
from conans.errors import ConanException
import os
import glob
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    @property
    def _test_shared_library(self):
        # shared library linking with static libnuma is not supported
        if "with_numa" in self.options["libx265"] and \
                bool(self.options["libx265"].with_numa) and \
                not bool(self.options["libnuma"].shared):
            return False
        try:
            return self.options["libx265"].fPIC
        except ConanException:
            return True

    def build(self):
        cmake = CMake(self)
        cmake.definitions["TEST_LIBRARY"] = self._test_shared_library
        cmake.configure()
        cmake.build()

    def test(self):
        # Copy all libraries to current and bin folderso we don't need any LD_LIBRARY_PATH/DYLD_LIBRARY_PATH/PATH (which might conflict with run_environment argument of self.run)
        for fn in glob.glob(os.path.join("lib", "*")):
            shutil.copy(src=fn, dst="bin")
            shutil.copy(src=fn, dst=".")
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
