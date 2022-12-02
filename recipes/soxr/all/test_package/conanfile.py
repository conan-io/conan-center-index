import os
from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            # core component
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package_core")
            self.run(bin_path, env="conanrun")
            # lsr component
            if self.dependencies[self.tested_reference_str].options.with_lsr_bindings:
                bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package_lsr")
                self.run(bin_path, env="conanrun")
