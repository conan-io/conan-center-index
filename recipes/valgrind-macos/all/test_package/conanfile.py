from conan import ConanFile
from conan.tools.build import can_run
import sys


class TestPackageConan(ConanFile):
    settings = "os", "arch"
    generators = "VirtualRunEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        if can_run(self):
            self.run("valgrind --version",
                     cwd=self.source_folder, run_environment=True)
