import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        # Mirror the tested package's with_host option: the plugin_host
        # component only exists when the package was built with it, so the
        # consumer must only link plotjuggler_sdk::plugin_host in that case.
        with_host = bool(self.dependencies["plotjuggler_sdk"].options.with_host)
        tc = CMakeToolchain(self)
        tc.cache_variables["TEST_WITH_HOST"] = with_host
        tc.generate()
        CMakeDeps(self).generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")
