from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.scm import Version
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)
    
    @property
    def _single_header_only(self):
        return self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "8"

    def generate(self):
        tc = CMakeToolchain(self)
        if self._single_header_only:
            tc.variables["TOMLPP_BUILD_SINGLE_ONLY"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            conf_path = os.path.join(self.source_folder, "configuration.toml")
            self.run(f"{bin_path} {conf_path}", env="conanrun")
            if not self._single_header_only:
                bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package_multi")
                self.run(f"{bin_path} {conf_path}", env="conanrun")
