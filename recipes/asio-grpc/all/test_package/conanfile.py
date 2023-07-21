from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout, CMakeDeps, CMakeToolchain
from conan.tools.env import VirtualRunEnv
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps",   "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)


    def generate(self):
        tc = CMakeToolchain(self)
        if self.dependencies["asio-grpc"].options.grpc_link == "none":
            #need to manually link the grpc library, add an option to tell cmake to do that
            tc.cache_variables["GRPC_LINK_MANUAL"] = True

        tc.generate()

    def build(self):
        cmake = CMake(self)

        envvars = VirtualRunEnv(self).vars()
        cmake.configure()
        with envvars.apply():
            cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
