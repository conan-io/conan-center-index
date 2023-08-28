import os
import shutil

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import chdir


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"
    exports_sources = "a.cpp", "b.cpp", "main.c", "main.cpp", "wscript"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

        buildenv = VirtualBuildEnv(self)
        buildenv.generate()

        env = Environment()
        for var in ["DYLD_LIBRARY_PATH", "LD_LIBRARY_PATH"]:
            env.append_path(var, os.path.join(self.build_folder, "build"))
        env.vars(self, scope="run").save_script("conanrun_macos_runtimepath")

        runenv = VirtualRunEnv(self)
        runenv.generate()

    def build(self):
        if not can_run(self):
            return

        for src in self.exports_sources:
            shutil.copy(os.path.join(self.source_folder, src), self.build_folder)

        with chdir(self, self.build_folder):
            self.run("waf -h")
            self.run("waf configure")
            self.run("waf")

    def test(self):
        if not can_run(self):
            return
        bin_dir = os.path.join(self.build_folder, "build")
        bin_path = os.path.join(bin_dir, "app")
        self.run(bin_path, env="conanrun")
        bin_path = os.path.join(bin_dir, "app2")
        self.run(bin_path, env="conanrun")
