import os

from conans import CMake, ConanFile, RunEnvironment, tools


class RootTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = ("cmake_paths", "cmake_find_package")
    requires = ("catch2/2.13.3",)

    def build(self):
        env_build = RunEnvironment(self)
        with tools.environment_append(env_build.vars):
            cmake = CMake(self)
            cmake.configure(defs={"CMAKE_VERBOSE_MAKEFILE": "ON"})
            cmake.build()

    def test(self):
        if not tools.cross_building(self):
            # self.run("ctest .", run_environment=True)
            self.run(f".{os.sep}example", run_environment=True)
