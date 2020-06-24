from conans import ConanFile, tools
import os
import shutil


class TestPackage(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def build(self):
        for f in ("header.h", "main.c", "source.c", "Jamfile"):
            shutil.copy(os.path.join(self.source_folder, f),
                        os.path.join(self.build_folder, f))
        if not tools.cross_building(self.settings):
            assert os.path.isfile(os.environ["JAM"])

            self.run(os.environ["JAM"])

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join(".", "test_package")
            self.run(bin_path, run_environment=True)
