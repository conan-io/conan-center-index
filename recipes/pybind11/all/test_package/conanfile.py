from conans import ConanFile, CMake, tools
import os
import sys


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        tools.replace_in_file(os.path.join(self.build_folder, "Findpybind11.cmake"),
                              "set_property(TARGET pybind11::pybind11 APPEND PROPERTY",
                              "")
        tools.replace_in_file(os.path.join(self.build_folder, "Findpybind11.cmake"),
                              "INTERFACE_LINK_LIBRARIES \"${pybind11_COMPONENTS}\")",
                              "")
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
                self.run("{} {}".format(self._python_interpreter, os.path.join(
                    self.source_folder, "test.py")), run_environment=True)
