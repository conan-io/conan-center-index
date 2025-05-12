import importlib
import os
import sys
from pathlib import PurePath

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain, CMakeDeps
from conan.tools.env import VirtualRunEnv
from conan.tools.microsoft import is_msvc


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str, visible=False, run=True)

    def layout(self):
        cmake_layout(self)

    @property
    def _can_build(self):
        # FIXME: Python does not distribute debug libraries (use cci CPython recipe)
        if is_msvc(self) and self.settings.build_type == "Debug":
            return False
        # FIXME: apple-clang fails with 'ld: library not found for -lintl' in CI, despite working ok locally
        if self.settings.compiler == "apple-clang":
            return False
        return True

    @property
    def _python_interpreter(self):
        if getattr(sys, "frozen", False):
            return "python"
        return sys.executable

    def generate(self):
        venv = VirtualRunEnv(self)
        venv.generate(scope="build")
        venv.generate(scope="run")
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
        sys.path.append(os.path.join(self.build_folder, str(self.settings.build_type)))
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
