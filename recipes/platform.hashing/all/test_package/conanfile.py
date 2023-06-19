from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMakeToolchain, CMake
import os

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    @property
    def _extra_flags(self):
        return self.dependencies["platform.hashing"].cpp_info.get_property("suggested_flags")

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        if str(self.settings.compiler) != "msvc" and self._extra_flags:
            tc = CMakeToolchain(self)
            tc.variables["EXTRA_FLAGS"] = self._extra_flags
            tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
