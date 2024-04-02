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
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        self.run("eu-ar --version", env="conanbuild")
        bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
        archive_path = "archive.a"
        self.run(f"eu-ar r {archive_path} {bin_path}", env="conanbuild")
        self.run(f"eu-objdump -d {bin_path}", env="conanbuild")
        if can_run(self):
            self.run(f"{bin_path} {bin_path}", env="conanrun")
            self.run(f"{bin_path} {archive_path}", env="conanrun")
