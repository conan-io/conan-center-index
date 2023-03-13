from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.layout import basic_layout

import os
import sys

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        basic_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.source_folder, "test_package.py")
            self.run(f"{sys.executable} {bin_path}", env="conanrun")
