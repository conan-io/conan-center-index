import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.build import can_run
from conan.tools.env import VirtualRunEnv

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        # Environment so that the compiled test executable can load shared libraries
        runenv = VirtualRunEnv(self)
        runenv.generate(scope="run")
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not can_run(self):
            return
        for test in ["bigtable", "pubsub", "spanner", "speech", "storage"]:
            cmd = os.path.join(self.cpp.build.bindir, test)
            self.run(cmd, env="conanrun")
