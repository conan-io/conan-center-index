from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
import os
import subprocess
import re


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

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
        if self.dependencies[self.tested_reference_str].options.build_executable:
            ext = ".exe" if self.settings.os == "Windows" else ""
            assert os.path.exists(os.path.join(self.dependencies[self.tested_reference_str].cpp_info.bindir, f"curl{ext}"))

        if can_run(self):
            self.run(self._test_executable, env="conanrun")
            if self.dependencies[self.tested_reference_str].options.build_executable:
                self.run("curl --version", env="conanrun")
