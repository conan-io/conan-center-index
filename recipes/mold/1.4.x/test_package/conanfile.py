import os
from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.layout import basic_layout


class MoldTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    # VirtualRunEnv can be avoided if "tools.env.virtualenv:auto_use" is defined
    # (it will be defined in Conan 2.0)
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        if not cross_building(self):
            self.run("mold -v")

