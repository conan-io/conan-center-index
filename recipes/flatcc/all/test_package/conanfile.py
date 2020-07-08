import os.path

from conans import ConanFile, CMake, tools, RunEnvironment


class FlatccTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        env_build = RunEnvironment(self)
        with tools.environment_append(env_build.vars):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join(self.build_folder, "bin", "monster")
            self.run(bin_path, cwd=self.source_folder, run_environment=True)
