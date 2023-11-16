import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain, CMakeDeps
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualRunEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["IGN_CMAKE_VER"] = Version(self.dependencies.build["ignition-cmake"].ref.version).major
        tc.generate()
        deps = CMakeDeps(self)
        deps.build_context_activated = ["ignition-cmake"]
        deps.build_context_build_modules = ["ignition-cmake"]
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            if is_msvc(self):
                bin_path = os.path.join(self.build_folder, "bin", str(self.settings.build_type), "test_package")
            else:
                bin_path = os.path.join(self.build_folder, "bin", "test_package")
            self.run(bin_path, env="conanrun")
