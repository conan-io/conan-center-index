from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
import os
import subprocess
import re


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @property
    def _test_executable(self):
        return os.path.join(self.cpp.build.bindirs[0], "test_package")

    def test(self):
        if can_run(self):
            self.run(self._test_executable, env="conanrun")
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
