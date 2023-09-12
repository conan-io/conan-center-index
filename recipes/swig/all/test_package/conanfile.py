import importlib
import sys
from pathlib import PurePath

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain, CMakeDeps
from conan.tools.microsoft import is_msvc


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    @property
    def _can_build(self):
        # FIXME: Python does not distribute debug libraries (use cci CPython recipe)
        return not (is_msvc(self) and self.settings.build_type == "Debug")

    @property
    def _python_interpreter(self):
        if getattr(sys, "frozen", False):
            return "python"
        return sys.executable

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["Python_EXECUTABLE"] = PurePath(self._python_interpreter).as_posix()
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        if can_run(self):
            self.run("swig -swiglib")
            if self._can_build:
                cmake = CMake(self)
                cmake.configure()
                cmake.build()

    def _test_swig_module(self):
        sys.path.append(self.build_folder)
        # Could also simply use 'import PackageTest' but this makes pylint angry
        PackageTest = importlib.import_module("PackageTest")
        assert PackageTest.gcd(12, 16) == 4
        self.output.info("PackageTest.gcd(12, 16) ran successfully")
        assert PackageTest.cvar.foo == 3.14159265359
        self.output.info("PackageTest.cvar.foo == 3.14159265359 ran successfully")
        sys.path.pop()

    def test(self):
        if can_run(self):
            if self._can_build:
                self._test_swig_module()
            self.run("swig -version")
            self.run("swig -swiglib")
