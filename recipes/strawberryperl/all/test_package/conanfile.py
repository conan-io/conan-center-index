from conan import ConanFile
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        self.run("perl --version")
        perl_script = os.path.join(self.source_folder, "list_files.pl")
        self.run(f"perl {perl_script}")
