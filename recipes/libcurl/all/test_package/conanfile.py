import os
import subprocess
import re

from conans import ConanFile, tools
from conan.tools.cmake import CMake
from conan.tools.layout import cmake_layout


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"

    def build(self):
        if tools.cross_building(self.settings) and self.settings.os in ["iOS"]:
            return  # on iOS I do not even need to build, it will just give am a and error about unsigned binaries
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def layout(self):
        cmake_layout(self)

    @property
    def _test_executable(self):
        if self.settings.os == "Windows":
            return os.path.join(self.cpp.build.bindirs[0], "test_package.exe")
        else:
            return os.path.join(self.cpp.build.bindirs[0], "test_package")

    def test(self):
        if not tools.cross_building(self):
            self.run(self._test_executable, env="conanrunenv")
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
