from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.scm import Version
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            tested_version = self.tested_reference_str.split('/')[1].split('@')[0]
            print('package version: ' + tested_version)
            if Version(tested_version) >= Version("3.0.0"):
                print(f'Skipping tests in version {tested_version}')
            else:
                bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
                self.run(bin_path, env="conanrun")
