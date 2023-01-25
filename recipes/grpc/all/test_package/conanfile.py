from conan import ConanFile
from conan.tools.build import can_run, cross_building
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
from conan.tools.env import VirtualRunEnv
from conan.tools.microsoft import is_msvc
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        # For the grpc-cpp-plugin executable
        self.tool_requires(self.tested_reference_str)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["TEST_ACTUAL_SERVER"] = not (is_msvc(self)
                                                        and str(self.settings.compiler.version) in ("15", "191")
                                                        and self.settings.build_type == "Release")
        tc.generate()
        
        # Set up environment so that we can run grpc-cpp-plugin at build time
        if not cross_building(self):
            VirtualRunEnv(self).generate(scope="build")
        
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
