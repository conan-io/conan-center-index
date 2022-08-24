from conan import ConanFile, tools
from conans import CMake
import os

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["OGRE_VERSION"] = tools.scm.Version(self, self.deps_cpp_info["ogre"].version)
        cmake.configure()
        cmake.build()

    def test(self):
        if tools.build.cross_building(self, self):
            return
 
        ogre_main_bin_path = os.path.join("bin", "ogre_main")
        self.run(ogre_main_bin_path, run_environment=True)
