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
        # Don't add Cargo dependencies to the global Cargo cache
        env.define_path("CARGO_HOME", os.path.join(self.build_folder, "cargo"))
        # Output location of the built binaries
        env.define_path("CARGO_TARGET_DIR", self.cpp.build.bindir)
        env.vars(self).save_script("cargo_build_env")

    def build(self):
        if can_run(self):
            self.run("rustc --version")
            self.run("cargo build --release")

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "release", "greetings")
            self.run(bin_path, env="conanrun")
