from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.env import VirtualRunEnv
import os

class TestPackageHazelcastCppClient(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.variables["HAZELCAST_CPP_CLIENT_VERSION"] = self.dependencies["hazelcast-cpp-client"].ref.version
        toolchain.generate()

        deps = CMakeDeps(self)
        deps.generate()

        runenv = VirtualRunEnv(self)
        runenv.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            self.run(os.path.join(self.cpp.build.bindirs[0], "test_package"), env="conanrun")
