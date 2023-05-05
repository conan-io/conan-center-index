from conans import ConanFile, CMake, tools

import os
from pathlib import PurePath
import sys

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        # Used by FindPython.cmake in CMake
        cmake.definitions["Python_EXECUTABLE"] = PurePath(self._python_interpreter).as_posix()
        # Used by FindPythonLibsNew.cmake in pybind11
        cmake.definitions["PYTHON_EXECUTABLE"] = PurePath(self._python_interpreter).as_posix()
        cmake.configure()
        cmake.build()

    @property
    def _python_interpreter(self):
        if getattr(sys, "frozen", False):
            return "python"
        return sys.executable

    def test(self):
        if not tools.cross_building(self):
            pythonpath = os.path.join(self.build_folder, self.cpp.build.libdirs[0])
            with tools.environment_append({"PYTHONPATH": pythonpath}):
                python_module = os.path.join(self.source_folder, "..", "test_package", "test.py")
                self.run(f"{self._python_interpreter} {python_module}", run_environment=True)
