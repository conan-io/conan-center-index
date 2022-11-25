from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
from conan.tools.env import VirtualRunEnv
from conan.tools.build import can_run
from conan.tools.layout import cmake_layout
from conans.tools import environment_append

import os
from pathlib import PurePath
import sys


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        toolchain = CMakeToolchain(self)
        toolchain.variables["PYTHON_EXECUTABLE"] = PurePath(self._python_interpreter).as_posix()
        toolchain.generate()

        run = VirtualRunEnv(self)
        run.generate()

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @property
    def _python_interpreter(self):
        if getattr(sys, "frozen", False):
            return "python"
        return sys.executable

    def test(self):
        if can_run(self):
            python_path = os.path.join(self.build_folder, self.cpp.build.libdirs[0])
            with environment_append({"PYTHONPATH": python_path}):
                module_path = os.path.join(self.source_folder, "test.py")
                self.run(f"{self._python_interpreter} {module_path}", env="conanrun")
