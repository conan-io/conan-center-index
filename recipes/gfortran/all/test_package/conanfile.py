import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMakeToolchain, CMake
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        buildenv = VirtualBuildEnv(self)
        buildenv.generate()

        # Hack to avoid adding tool_requires(self.tested_reference_str),
        # which tends to fail with a missing binaries error
        runenv = VirtualRunEnv(self)
        runenv.generate(scope="build")
        runenv.generate(scope="run")

        tc = CMakeToolchain(self)
        tc.generate()


    def build(self):
        if can_run(self):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if can_run(self):
            self.run("$FC --version", env="conanbuild")
            self.run("$FC -dumpversion", env="conanbuild")
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")
