import os

from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.build import can_run, cross_building
from conan.tools.env import VirtualRunEnv, VirtualBuildEnv
from conan.tools.layout import basic_layout
from conan.tools.microsoft import unix_path


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        basic_layout(self)

    def test(self):
        if can_run(self):
            self.run("gn help", env="conanrun")
