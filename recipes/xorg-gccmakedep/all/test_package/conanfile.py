from conan import ConanFile
from conan.errors import ConanException
from conan.tools.files import copy, load
from conan.tools.layout import basic_layout
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "Makefile", "test_package.c", "test_package.h"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        basic_layout(self)

    def build(self):
        for src in self.exports_sources:
            copy(self, src, self.source_folder, self.build_folder)

        src = os.path.join(self.build_folder, "test_package.c")
        self.run(f"gccmakedep {src}", env="conanbuild")

        if load(self, os.path.join(self.source_folder, "Makefile")) == os.path.join(self.build_folder, "Makefile"):
            raise ConanException("xorg-gccmakedep did not modify `Makefile'")

    def test(self):
        pass
