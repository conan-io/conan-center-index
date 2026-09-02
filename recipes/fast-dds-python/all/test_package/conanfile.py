import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.layout import basic_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        basic_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        if can_run(self):
            python = "python" if self.settings.os == "Windows" else "python3"
            test_script = os.path.join(self.source_folder, "test.py")
            self.run(f'{python} "{test_script}"', env="conanrun")
