import os

from conans import ConanFile, tools


class GoogleguetzliTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def test(self):
        bees_path = os.path.join(self.source_folder, os.pardir, "test_package", "bees.png")
        if not tools.cross_building(self.settings):
            self.run(f"guetzli --quality 84 {bees_path} bees.jpg", run_environment=True)
