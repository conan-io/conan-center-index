import os
from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.env import VirtualBuildEnv
from conan.tools.scm import Version


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        if can_run(self):
            self.run("perl --version")
            perl_script = os.path.join(self.source_folder, "list_files.pl")
            self.run(f"perl {perl_script}", env="conanbuild")
