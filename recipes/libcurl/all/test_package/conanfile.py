from conan import ConanFile, tools
from conans import CMake
import os
import subprocess
import re


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build_requirements(self):
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            # Workaround for CMake bug with error message:
            # Attempting to use @rpath without CMAKE_SHARED_LIBRARY_RUNTIME_C_FLAG being
            # set. This could be because you are using a Mac OS X version less than 10.5
            # or because CMake's platform configuration is corrupt.
            # FIXME: Remove once CMake on macOS/M1 CI runners is upgraded.
            self.build_requires("cmake/3.22.0")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @property
    def _test_executable(self):
        if self.settings.os == "Windows":
            return os.path.join("bin", "test_package.exe")
        else:
            return os.path.join("bin", "test_package")

    def test(self):
        if not tools.build.cross_building(self, self):
            self.run(self._test_executable, run_environment=True)
        else:
            # We will dump information for the generated executable
            if self.settings.os in ["Android", "iOS"]:
                # FIXME: Check output for these hosts
                return

            output = subprocess.check_output(["file", self._test_executable]).decode()

            if self.settings.os == "Macos" and self.settings.arch == "armv8":
                assert "Mach-O 64-bit executable arm64" in output, "Not found in output: {}".format(output)

            elif self.settings.os == "Linux":
                if self.settings.arch == "armv8_32":
                    assert re.search(r"Machine:\s+ARM", output), "Not found in output: {}".format(output)
                elif "armv8" in self.settings.arch:
                    assert re.search(r"Machine:\s+AArch64", output), "Not found in output: {}".format(output)
                elif "arm" in self.settings.arch:
                    assert re.search(r"Machine:\s+ARM", output), "Not found in output: {}".format(output)

            elif self.settings.os == "Windows": # FIXME: It satisfies not only MinGW
                assert re.search(r"PE32.*executable.*Windows", output), "Not found in output: {}".format(output)
