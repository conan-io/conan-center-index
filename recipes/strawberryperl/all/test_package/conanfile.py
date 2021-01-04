import os
from conans import ConanFile


class DefaultNameConan(ConanFile):
    settings = "os", "arch"

    def test(self):
        self.run("perl --version")
        perl_script = os.path.join(self.source_folder, "list_files.pl")
        self.run("perl {}".format(perl_script), run_environment=True)
