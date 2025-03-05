from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"

    @property
    def _tested_modules(self):
        return ["azure-core",
                "azure-storage-common",
                "azure-storage-blobs",
                "azure-storage-files-shares"]

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
            for module in self._tested_modules:
                bin_path = os.path.join(self.cpp.build.bindirs[0], f"test_{module}")
                self.run(bin_path, env="conanrun")
