import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        tc = CMakeToolchain(self)
        backend = str(self.dependencies["stdgpu"].options.backend)
        tc.variables["STDGPU_BACKEND"] = backend
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            for variant in ["basic", "openmp", "cuda"]:
                bin_path = os.path.join(self.cpp.build.bindir, f"test_package_{variant}")
                if os.path.exists(bin_path):
                    self.run(bin_path, env="conanrun")
