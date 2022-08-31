from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "MesonToolchain", "VirtualBuildEnv", "VirtualRunEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.build_requires(self.tested_reference_str)

    def layout(self):
        basic_layout(self)

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def test(self):
        self.run("meson --version")
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
