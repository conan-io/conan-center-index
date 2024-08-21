import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.build import can_run
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.scm import Version


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    @property
    def _is_legacy_one_profile(self):
        return not hasattr(self, "settings_build")

    def layout(self):
        cmake_layout(self)
    
    def _supports_compute(self):
        if not hasattr(self, "dependencies"):
            # This is typically a Conan v1 build. We skip the test for compute
            # because it is difficult to establish the `google-cloud-cpp`
            # version, and Conan v1 is being retired, and the support is tested
            # as part of the Conan v2 build.
            return False
        return Version(self.dependencies["google-cloud-cpp"].ref.version) >= "2.19.0"

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["WITH_COMPUTE"] = self._supports_compute()
        tc.generate()
        if self._is_legacy_one_profile:
            VirtualRunEnv(self).generate(scope="build")
        else:
            VirtualBuildEnv(self).generate()
        # Environment so that the compiled test executable can load shared libraries
        VirtualRunEnv(self).generate(scope="run")
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not can_run(self):
            return
        for test in ["bigtable", "pubsub", "spanner", "speech", "storage"]:
            cmd = os.path.join(self.cpp.build.bindir, test)
            self.run(cmd, env="conanrun")
        if self._supports_compute():
            cmd = os.path.join(self.cpp.build.bindir, "compute")
            self.run(cmd, env="conanrun")
