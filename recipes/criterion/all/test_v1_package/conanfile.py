import os
from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.layout import basic_layout


class CriterionTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "PkgConfigDeps", "MesonToolchain"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        tc = MesonToolchain(self)
        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def layout(self):
        basic_layout(self)

    def test(self):
        if can_run(self):
            cmd = os.path.join(self.cpp.build.bindir, "example")
            self.run(cmd, env="conanrun")

    def build_requirements(self):
        self.tool_requires("meson/1.0.0")
        self.tool_requires("pkgconf/1.9.3")
