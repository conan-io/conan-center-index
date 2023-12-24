from conans import ConanFile, CMake, tools, RunEnvironment
import os

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self, toolset="cuda={}".format(self.deps_env_info["cudasdk"].CUDASDK_PATH))
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self.run(os.path.join("bin", "test_package"), run_environment=True)
