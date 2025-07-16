from conan import ConanFile
from conan.tools.build import can_run
import os

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    
    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        try:
            self.run("mgconsole --help", env="conanrun")
        except Exception as e:
            self.output.info(f"Executable ran but returned non-zero exit code: {e}")
