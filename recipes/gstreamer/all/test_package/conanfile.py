from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeDeps, CMakeToolchain
from conan.tools.env import Environment, VirtualRunEnv
from conan.tools.gnu import PkgConfigDeps
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        pkg_config_deps = PkgConfigDeps(self)
        pkg_config_deps.generate()
        cmake_deps = CMakeDeps(self)
        cmake_deps.generate()
        tc = CMakeToolchain(self)
        tc.generate()
        runenv = VirtualRunEnv(self)
        runenv.generate()

        # Print debug information from gstreamer at runtime
        env = Environment()
        env.define("GST_DEBUG", "7")
        env.vars(self, scope="run").save_script("conanrun_gstdebug")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
