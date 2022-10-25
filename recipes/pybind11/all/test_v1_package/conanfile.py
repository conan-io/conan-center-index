from conans import ConanFile, CMake, tools
import os
import sys
from platform import python_version


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

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
        if not tools.cross_building(self):
            with tools.environment_append({"PYTHONPATH": "lib"}):
                python_module = os.path.join(self.source_folder, "..", "test_package", "test.py")
                self.run(f"{self._python_interpreter} {python_module}", run_environment=True)
