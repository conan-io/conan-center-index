from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_ext = ".exe" if self.settings.os == "Windows" else ""
            bin_path = os.path.join(self.cpp.build.bindir, f"test_package{bin_ext}")

            self.run(f"upx --help")

            original_size = os.stat(bin_path).st_size

            self.run(f"upx {bin_path}")

            packed_size = os.stat(bin_path).st_size

            # Run the packed executable to see whether it still works
            self.run(bin_path, env="conanrun")

            self.output.info(f"File: {bin_path}")
            self.output.info(f"Original size: {original_size:>9}")
            self.output.info(f"Packed size:   {packed_size:>9}")
            self.output.info(f"               ---------")
            self.output.info(f"Size diff:     {original_size-packed_size:>9}")
