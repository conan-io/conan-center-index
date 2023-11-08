import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def build(self):
        if can_run(self):
            self.run("rustc --version")
            os.environ["CARGO_TARGET_DIR"] = "."
            self.run("cargo build --release")

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "release", "greetings")
            self.run(bin_path, env="conanrun")
