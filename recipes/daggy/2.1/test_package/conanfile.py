import os

from conans import ConanFile, CMake, tools, RunEnvironment


class DaggyTestConan(ConanFile):
    name = "daggy_test"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_paths", "cmake_find_package"

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "with_ssh2": [True, False],
        "with_yaml": [True, False],
        "with_console": [True, False],
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "with_ssh2": True,
        "with_yaml": True,
        "with_console": False,
        "shared": False,
        "fPIC": True
    }

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self.run(os.path.join("bin", "testcpp"), run_environment=True)
