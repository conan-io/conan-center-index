from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
import os


class NsyncTestConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
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
            test_package_c = os.path.join(self.cpp.build.bindirs[0], "test_package")
            test_package_cpp = os.path.join(self.cpp.build.bindirs[0], "test_package_cpp")
            self.run(test_package_c, env="conanrun")
            self.run(test_package_cpp, env="conanrun")
