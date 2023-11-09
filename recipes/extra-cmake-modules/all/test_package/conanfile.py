from conan import ConanFile, conan_version
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        # CMakeToolchain of conan v1 doesn't add cpp_info.builddirs of build requirements to CMAKE_PREFIX_PATH
        if conan_version < "2":
            self.requires(self.tested_reference_str)

    def build_requirements(self):
        if conan_version >= "2":
            self.tool_requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
