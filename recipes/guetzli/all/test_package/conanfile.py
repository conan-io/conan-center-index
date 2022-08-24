import os

from conans import ConanFile, tools


class GoogleguetzliTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def test(self):
        bees_path = os.path.join(self.source_folder, "bees.png")
        if not tools.build.cross_building(self, self.settings):
            app = "guetzli"
            if self.settings.os == "Windows":
                app += ".exe"
            self.run("{} --quality 84 {} bees.jpg".format(app, bees_path),
                     run_environment=True)
