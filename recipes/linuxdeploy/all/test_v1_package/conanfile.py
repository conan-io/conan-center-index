from conans import ConanFile, CMake, tools, RunEnvironment
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        env_build = RunEnvironment(self) # add linuxdeploy to path
        with tools.environment_append(env_build.vars):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self.output.info(f"Running AppRun inside AppDir: {os.path.join(self.build_folder, 'test_package', 'AppDir', 'AppRun')}")
            self.run(os.path.join(self.build_folder, "test_package", "AppDir", "AppRun"), run_environment=False)
