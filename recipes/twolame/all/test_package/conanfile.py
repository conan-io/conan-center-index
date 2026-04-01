from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.files import copy
from conan.tools.cmake import cmake_layout, CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        is_shared = self.dependencies[self.tested_reference_str].options.get_safe("shared", False)
        is_windows = self.dependencies[self.tested_reference_str].settings.os == "Windows"
        if is_shared and is_windows:
            copy(self, pattern="*.dll", src=os.path.join(self.dependencies[self.tested_reference_str].package_folder, "lib"), dst=self.cpp.build.bindir)

        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")
