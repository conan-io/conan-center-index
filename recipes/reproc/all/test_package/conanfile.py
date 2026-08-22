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
        tc.variables["WITH_CXX"] = self.dependencies["reproc"].options.get_safe("cxx")
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package_c")
            self.run(bin_path, env="conanrun")
            if (self.dependencies["reproc"].options.get_safe("cxx")):
                bin_path = os.path.join(self.cpp.build.bindir, "test_package_cpp")
                self.run(bin_path, env="conanrun")
