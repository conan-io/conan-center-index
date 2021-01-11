import os
from conans import ConanFile, tools


class DefaultNameConan(ConanFile):
    settings = "os", "arch"

    def test(self):
        if not tools.cross_building(self):
            self.run("perl --version", run_environment=True)
            perl_script = os.path.join(self.source_folder, "list_files.pl")
            self.run("perl {}".format(perl_script), run_environment=True)
