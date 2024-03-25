from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
import pathlib

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cm = CMake(self)
        cm.configure()
        cm.build()

    def test(self):
        if can_run(self):
            bin_path = pathlib.Path(self.build_folder) / "test_package"
            print(str(bin_path))
            self.run(bin_path, env="conanrun")
