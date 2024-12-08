from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os


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
        tc.variables["QHULL_REENTRANT"] = self.dependencies["qhull"].options.get_safe("reentrant", True)
        tc.variables["QHULL_CPP"] = self.dependencies["qhull"].options.get_safe("cpp", False)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")

            bin_path = os.path.join(self.cpp.build.bindir, "test_package_cpp")
            if os.path.exists(bin_path):
                self.run(bin_path, env="conanrun")
