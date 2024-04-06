from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["WITH_UTILITY"] = self.dependencies["corrade"].options.with_utility
        if self.dependencies["corrade"].ref.version == "2019.10":
            tc.variables["VERSION_2019_10"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")

        if self.settings.os == "Emscripten":
            bin_path = os.path.join(self.cpp.build.bindir, "test_package.js")
            self.run(f"node {bin_path}", env="conanrun")
