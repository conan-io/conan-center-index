from conan import ConanFile, conan_version
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
import os


class TestPackageConan(ConanFile):
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
            if conan_version.major >= 2:
                usingz = self.dependencies["clipper2"].options.usingz
            else:
                usingz = self.options["clipper2"].usingz

            if usingz != "ONLY":
                bin_path = os.path.join(self.cpp.build.bindir, "test_package")
                self.run(bin_path, env="conanrun")
            if usingz != "OFF":
                bin_path = os.path.join(self.cpp.build.bindir, "test_package_z")
                self.run(bin_path, env="conanrun")
