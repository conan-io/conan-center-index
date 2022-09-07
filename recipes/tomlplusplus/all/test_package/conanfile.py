from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.scm import Version
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        if Version(self.deps_cpp_info["tomlplusplus"].version) < "1.3.0":
            self.single_header_only = True
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "8":
            self.single_header_only = True
        variables = {"TOMLPP_BUILD_SINGLE_ONLY": True} if hasattr(self, "single_header_only") else None
        cmake.configure(variables=variables)
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(f"{bin_path} ../../configuration.toml", env="conanrun")
            if not hasattr(self, "single_header_only"):
                bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package_multi")
                self.run(f"{bin_path} ../../configuration.toml", env="conanrun")
