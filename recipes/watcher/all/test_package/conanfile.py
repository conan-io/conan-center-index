from conan import ConanFile
from conan.tools.cmake import cmake_layout, CMake
from conan.tools.build import can_run
from conan.tools.env import Environment

import os
import subprocess

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

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            env_vars = Environment().vars(self, scope="conanrun")
            try:
                # Because watcher API never returns, we have to set timeout
                subprocess.run([bin_path], timeout=3, env=env_vars)
            except subprocess.TimeoutExpired:
                pass
