from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str, run=True)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            self.run("slangc -version", env="conanrun")

            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            slang_path = os.path.join(self.source_folder, "hello_world.slang")
            self.run(f"{bin_path} {slang_path}", env="conanrun")
