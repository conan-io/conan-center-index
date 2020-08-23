from conans import ConanFile, CMake, tools
import os
import sys


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["PYTHON_EXECUTABLE"] = self._python_interpreter
        cmake.configure()
        cmake.build()

    @property
    def _python_interpreter(self):
        if getattr(sys, "frozen", False):
            return "python"
        return sys.executable

    def test(self):
        if not tools.cross_building(self.settings):
            with tools.environment_append({"PYTHONPATH": "lib"}):
                self.run("{} {}".format(self._python_interpreter, os.path.join(self.source_folder, "test.py")), run_environment=True)
