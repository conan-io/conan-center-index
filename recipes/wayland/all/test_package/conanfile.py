import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout, CMakeDeps, CMakeToolchain
from conan.tools.env import VirtualBuildEnv
from conan.tools.gnu import PkgConfig, PkgConfigDeps


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    test_type = "explicit"

    @property
    def _has_build_profile(self):
        return hasattr(self, "settings_build")

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/1.9.3")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        cmake_deps = CMakeDeps(self)
        cmake_deps.generate()
        pkg_config_deps = PkgConfigDeps(self)
        if self._has_build_profile:
            pkg_config_deps.build_context_activated = ["wayland"]
            pkg_config_deps.build_context_suffix = {"wayland": "_BUILD"}
        pkg_config_deps.generate()
        virtual_build_env = VirtualBuildEnv(self)
        virtual_build_env.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

        if self._has_build_profile:
            pkg_config = PkgConfig(self, "wayland-scanner_BUILD", self.generators_folder)
            wayland_scanner = pkg_config.variables["wayland_scanner"]
            self.run(f"{wayland_scanner} --version", env="conanrun")

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
