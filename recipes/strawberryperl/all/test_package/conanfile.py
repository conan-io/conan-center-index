import os
from conan import ConanFile
from conan.tools.build import can_run


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def test(self):
        if can_run(self):
            self.run("perl --version", run_environment=True)
            perl_script = os.path.join(self.source_folder, "list_files.pl")
            self.run(f"perl {perl_script}", run_environment=True)
