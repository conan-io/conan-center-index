import os
import shutil

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.files import mkdir, rm
from conan.tools.layout import basic_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualRunEnv", "VirtualBuildEnv"
    test_type = "explicit"

    _targets = ("c64", "apple2")

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        basic_layout(self)

    def build(self):
        if can_run(self):
            for src in ["hello.c", "text.s"]:
                shutil.copy(os.path.join(self.source_folder, src), os.path.join(self.build_folder, src))
            for target in self._targets:
                output = f"hello_{target}"
                mkdir(self, target)
                rm(self, output, self.build_folder)
                self.run(f"cc65 -O -t {target} hello.c -o {target}/hello.s")
                self.run(f"ca65 -t {target} {target}/hello.s -o {target}/hello.o")
                self.run(f"ca65 -t {target} text.s -o {target}/text.o")
                self.run(f"ld65 -o {output} -t {target} {target}/hello.o {target}/text.o {target}.lib")

    def test(self):
        if can_run(self):
            for target in self._targets:
                assert os.path.isfile(f"hello_{target}")
