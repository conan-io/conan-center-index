import os

from conans import ConanFile, tools


class TestPackageConan(ConanFile):
    settings = "os"

    def test(self):
        if tools.cross_building(self.settings):
            return
        bloaty_path = os.path.join(self.deps_cpp_info["bloaty"].bin_paths[0], "bloaty")
        self.run("bloaty {}".format(bloaty_path), run_environment=True)
