import importlib
import sys
from pathlib import PurePath

from conans import CMake, ConanFile, tools


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    @property
    def _can_build(self):
        # FIXME: Python does not distribute debug libraries (use cci CPython recipe)
        if self.settings.compiler == "Visual Studio" and self.settings.build_type == "Debug":
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

    def build(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            self.run("swig -swiglib", run_environment=True)
            if self._can_build:
                cmake = CMake(self)
                cmake.verbose = True
                cmake.definitions["Python_EXECUTABLE"] = PurePath(self._python_interpreter).as_posix()
                cmake.configure()
                cmake.build()
                cmake.install()

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
        if not tools.cross_building(self):
            if self._can_build:
                self._test_swig_module()
            self.run("swig -version", run_environment=True)
