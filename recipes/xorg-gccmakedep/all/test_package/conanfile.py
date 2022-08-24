from conan import ConanFile, tools
from conans.errors import ConanException
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "Makefile", "test_package.c", "test_package.h"

    def build(self):
        for src in self.exports_sources:
            shutil.copy(os.path.join(self.source_folder, src), os.path.join(self.build_folder, src))

    def test(self):
        src = os.path.join(self.source_folder, "test_package.c")
        self.run("gccmakedep {}".format(src), run_environment=True)

        if tools.files.load(self, os.path.join(self.source_folder, "Makefile")) == os.path.join(self.build_folder, "Makefile"):
            raise ConanException("xorg-gccmakedep did not modify `Makefile'")
