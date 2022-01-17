import os

from conans import ConanFile, tools


class TestPackageConan(ConanFile):
    settings = ("os", "arch", "compiler", "build_type")

    def test(self):
        if not tools.cross_building(self):
            idl = os.path.join(self.source_folder, "idl.idl")
            self.run(f"cloop {idl} json idl.json", run_environment=True)
