from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    @property
    def _has_s3_dependency(self):
        return self.dependencies[self.tested_reference_str].options.s3

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SDK_HAS_S3"] = self._has_s3_dependency
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")

            if self._has_s3_dependency:
                s3_bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package_s3")
                self.run(s3_bin_path, env="conanrun")

