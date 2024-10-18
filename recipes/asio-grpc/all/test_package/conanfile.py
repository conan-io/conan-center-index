import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.env import VirtualRunEnv


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps"

    def requirements(self):
        self.requires(self.tested_reference_str)
        # Needed for asio_grpc_protobuf_generate()
        self.requires("protobuf/3.21.12")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        # Avoid "libgrpc_plugin_support.so.1.54: cannot open shared object file: No such file or directory"
        VirtualRunEnv(self).generate(scope="build")
        VirtualRunEnv(self).generate(scope="run")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")
