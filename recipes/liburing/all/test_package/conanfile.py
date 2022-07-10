from conans import ConanFile, CMake, tools
import os
import platform
import re


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @property
    def _sufficient_linux_kernel_version(self):
        # FIXME: use kernel version of build/host machine. kernel version should be encoded in profile
        linux_kernel_version = re.match("([0-9.]+)", platform.release()).group(1)
        return tools.Version(linux_kernel_version) >= "5.1"

    def test(self):
        if not tools.cross_building(self) and self._sufficient_linux_kernel_version:
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
