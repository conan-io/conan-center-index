from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    @property
    def _vulkan_sdk_version(self):
        return self.tested_reference_str.split("/")[1].split("#")[0]

    def requirements(self):
        self.requires(self.tested_reference_str, run=True)
        self.requires(f"vulkan-loader/{self._vulkan_sdk_version}")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            # Tests that the VkLayer_khronos_validation runtime library is loaded and used correctly
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")
