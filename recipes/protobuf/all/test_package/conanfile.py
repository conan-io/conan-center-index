from conans import ConanFile, CMake, tools
import os
from contextlib import contextmanager

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi", "VirtualRunEnv", "VirtualBuildEnv"

    def build_requirements(self):
        if hasattr(self, "settings_build"):
            self.build_requires(str(self.requires['protobuf']))

    @contextmanager
    def _env(self):
        if hasattr(self, "settings_build"):
            # 2 profiles - nothing is needed, VirtualRunEnv/VirtualBuildEnv manages the things
            yield
        else:
            from conans import RunEnvironment
            env_build = RunEnvironment(self)
            with tools.environment_append(env_build.vars):
                yield

    def build(self):
        with self._env():
            cmake = CMake(self)
            cmake.definitions["protobuf_LITE"] = self.options["protobuf"].lite
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("protoc --version", run_environment=True)

            self.run(os.path.join("bin", "test_package"), run_environment=True)
