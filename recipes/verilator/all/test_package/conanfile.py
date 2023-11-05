import os

from conan import ConanFile, conan_version
from conan.tools.apple import is_apple_os
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain, CMakeDeps
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import save, load
from conan.tools.scm import Version


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        if self._with_systemc_example:
            self.requires("systemc/2.3.4")

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)
        if self._with_systemc_example:
            self.tool_requires("systemc/<host_version>")

    def layout(self):
        cmake_layout(self)

    @property
    def _with_systemc_example(self):
        # systemc is not available on Macos
        if is_apple_os(self):
            return False
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "6":
            return False
        return True

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_SYSTEMC"] = self._with_systemc_example
        tc.generate()
        if hasattr(self, "settings_build"):
            VirtualBuildEnv(self).generate()
            deps = CMakeDeps(self)
            deps.build_context_activated = ["verilator"]
            deps.build_context_build_modules = ["verilator"]
            deps.generate()
        save(self, os.path.join(self.generators_folder, "verilator_path"),
             os.path.join(self.dependencies.build["verilator"].package_folder, "bin", "verilator"))

    def build(self):
        if can_run(self):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if not can_run(self):
            return
        verilator_path = load(self, os.path.join(self.generators_folder, "verilator_path"))
        self.run(f"perl {verilator_path} --version")
        bin_path = os.path.join(self.cpp.build.bindir, "blinky")
        self.run(bin_path, env="conanrun")
        if self._with_systemc_example:
            bin_path = os.path.join(self.cpp.build.bindir, "blinky_sc")
            self.run(bin_path, env="conanrun")
