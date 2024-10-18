from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
import os

from conan.tools.files import save, load


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        save(self, os.path.join(self.generators_folder, "cxx_enabled"),
             str(self.dependencies["libtiff"].options.get_safe("cxx_enabled", False)))

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        cxx_enabled = load(self, os.path.join(self.generators_folder, "cxx_enabled")) == "True"
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package_c")
            self.run(bin_path, env="conanrun")
            if cxx_enabled:
                bin_path = os.path.join(self.cpp.build.bindir, "test_package_cxx")
                self.run(bin_path, env="conanrun")
