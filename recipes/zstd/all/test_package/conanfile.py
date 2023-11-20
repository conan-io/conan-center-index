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

    def requirements(self):
        self.requires(self.tested_reference_str, run=True)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not can_run(self):
            return

        bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
        png_file = os.path.join(self.source_folder, "logo.png")
        self.run(f"{bin_path} {png_file}", env="conanrun")

        self.run(f"zstd --version", env="conanrun")
