import os

from conans import CMake, ConanFile, RunEnvironment, tools


class RootTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_find_package"

    def build(self):
        env_build = RunEnvironment(self)
        with tools.environment_append(env_build.vars):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self._check_binaries_are_found()
            self._check_root_dictionaries()

    def _check_binaries_are_found(self):
        self.run("root -q", run_environment=True)

    def _check_root_dictionaries(self):
        self.run(".{}testrootdictionaries".format(os.sep), run_environment=True)
