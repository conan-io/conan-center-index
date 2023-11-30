from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @property
    def _vulkan_sdk_version(self):
        return self.tested_reference_str.split("/")[1].split("#")[0]

    def requirements(self):
        self.requires(f"vulkan-loader/{self._vulkan_sdk_version}")

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
