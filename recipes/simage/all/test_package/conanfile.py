from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.build import can_run
import pathlib
import os
from io import StringIO


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps", "PkgConfigDeps"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cm = CMake(self)
        cm.configure()
        cm.build()

    def test(self):
        bindir = pathlib.Path(self.cpp.build.bindir).absolute()
        if can_run(self):
            bin_path_cm = str(bindir / "test_cmake_find")
            bin_path_pkc = str(bindir / "test_pkc_find")
            self.output.info("CMake find method test...")
            self.run(bin_path_cm, env="conanrun")
            self.output.info("pkg-config find method test...")
            self.run(bin_path_pkc, env="conanrun")
