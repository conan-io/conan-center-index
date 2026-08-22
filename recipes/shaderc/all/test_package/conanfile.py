import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str, run=True)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            # Test programs consuming shaderc lib
            bin_path_shaderc_c = os.path.join(self.cpp.build.bindir, "test_package_shaderc_c")
            self.run(bin_path_shaderc_c, env="conanrun")

            bin_path_shaderc_cpp = os.path.join(self.cpp.build.bindir, "test_package_shaderc_cpp")
            self.run(bin_path_shaderc_cpp, env="conanrun")

            # Test glslc executable
            self.run(f"glslc -h", env="conanrun")
