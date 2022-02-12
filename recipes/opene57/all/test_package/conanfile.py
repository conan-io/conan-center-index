import os
from conan.tools.microsoft import msvc_runtime_flag
from conans import ConanFile, CMake, tools

class TestOpenE57Conan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        if not tools.cross_building(self):
            cmake = CMake(self)
            cmake.definitions["BUILD_WITH_MT"] = "MT" in str(msvc_runtime_flag(self))
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "opene57_example")
            self.run(bin_path, run_environment=True)
