from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import Environment, VirtualRunEnv
from conan.tools.build import can_run

import os
from pathlib import PurePath
import sys


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        toolchain = CMakeToolchain(self)
        # Used by FindPython.cmake in CMake
        toolchain.variables["Python_EXECUTABLE"] = PurePath(self._python_interpreter).as_posix()
        # Used by FindPythonLibsNew.cmake in pybind11
        toolchain.variables["PYTHON_EXECUTABLE"] = PurePath(self._python_interpreter).as_posix()
        toolchain.generate()

        env = Environment()
        env.append_path("PYTHONPATH", os.path.join(self.build_folder, self.cpp.build.libdirs[0]))
        env.vars(self, scope="run").save_script("testrun")

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
            module_path = os.path.join(self.source_folder, "test.py")
            self.run(f"{self._python_interpreter} {module_path}", env="conanrun")
