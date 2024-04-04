import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout
from conan.tools.env import Environment
from conan.tools.microsoft import VCVars, is_msvc


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def generate(self):
        if is_msvc(self):
            VCVars(self).generate()

        env = Environment()
        env.define_path("CARGO_TARGET_DIR", self.build_folder)
        env.vars(self).save_script("cargo_target_dir")

    def build(self):
        if can_run(self):
            self.run("rustc --version")
            self.run("cargo build --release")

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.build_folder, "release", "greetings")
            self.run(bin_path, env="conanrun")
