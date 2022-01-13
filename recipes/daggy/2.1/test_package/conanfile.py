import os

from conans import ConanFile, CMake, tools, RunEnvironment


class DaggyTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_paths", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            env_build = RunEnvironment(self)
            with tools.environment_append(env_build.vars):
                os.chdir("bin")
                self.run(".%stestcpp" % os.sep)
                self.run(".%stestc" % os.sep)