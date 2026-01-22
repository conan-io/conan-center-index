import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout, CMakeDeps, CMakeToolchain
from conan.tools.gnu import PkgConfig, PkgConfigDeps


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[2.2 <3]")

    def layout(self):
        cmake_layout(self)

    @property
    def _wayland_libraries_enabled(self):
        return self.dependencies[self.tested_reference_str].options.get_safe("enable_libraries", False)

    @property
    def _wayland_scanner_enabled(self):
        return self.dependencies[self.tested_reference_str].options.get_safe("enable_scanner", True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CONAN_WAYLAND_LIBRARIES_ENABLED"] = self._wayland_libraries_enabled
        tc.generate()
        cmake_deps = CMakeDeps(self)
        cmake_deps.generate()
        pkg_config_deps = PkgConfigDeps(self)
        pkg_config_deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

        if self._wayland_scanner_enabled:
            pkg_config = PkgConfig(self, "wayland-scanner", self.generators_folder)
            wayland_scanner = pkg_config.variables["wayland_scanner"]
            if can_run(self):
                self.run(f"{wayland_scanner} --version", env="conanrun")

    def test(self):
        if can_run(self) and self._wayland_libraries_enabled:
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
