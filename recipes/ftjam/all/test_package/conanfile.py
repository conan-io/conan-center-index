import os
import shutil

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.layout import basic_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        basic_layout(self)

    def build(self):
        for f in ("header.h", "main.c", "source.c", "Jamfile"):
            shutil.copy(os.path.join(self.source_folder, f), os.path.join(self.build_folder, f))
        if can_run(self):
            self.run("jam -d7")

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")
