from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.scm import Version
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps", "VirtualRunEnv"

    def build_requirements(self):
        if Version(self.tested_reference_str.split('/')[1]) >= "4.1.0":
            self.tool_requires("cmake/[>=3.23 <4]")

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake_cxx_standard = 11 if Version(self.tested_reference_str.split('/')[1]) < "4.1.0" else 14
        cmake.configure(
            defs={
                "CMAKE_CXX_STANDARD": cmake_cxx_standard,
            }
        )
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
