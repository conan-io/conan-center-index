import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout, CMakeDeps, CMakeToolchain
from conan.tools.files import load
from conan.tools.gnu import PkgConfig, PkgConfigDeps


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def requirements(self):
        self.requires(self.tested_reference_str, run=True)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        cmake_deps = CMakeDeps(self)
        cmake_deps.generate()
        pkg_config_deps = PkgConfigDeps(self)
        pkg_config_deps.generate()

    def build(self):
        if self.dependencies["wayland"].options.enable_libraries:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

        wayland_scanner_pc = os.path.join(self.generators_folder, "wayland-scanner.pc")
        assert os.path.exists(wayland_scanner_pc)
        pc_contents = load(self, wayland_scanner_pc)
        assert "wayland_scanner=" in pc_contents

    def test(self):
        if can_run(self) and self.dependencies["wayland"].options.enable_libraries:
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")

        if can_run(self):
            self.run(f"wayland-scanner --version", env="conanrun")
