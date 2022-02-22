from conans import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.layout import cmake_layout
from conan.tools.env import Environment
from conan.tools.cross_building import cross_building
import os
import sys


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps"

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.variables["PYTHON_EXECUTABLE"] = self._python_interpreter.replace("\\", "/")
        toolchain.variables["PYBIND_VERSION"] = str(self.dependencies["pybind11"].ref.version)
        toolchain.generate()

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
        if not cross_building(self):
            env = Environment()
            env.define("PYTHONPATH", self.cpp.build.libdirs[0])
            env.vars(self).save_script("launcher")
            test_path = os.path.join(self.source_folder, "test.py")
            self.run("{} {}".format(self._python_interpreter, test_path), env="launcher")

