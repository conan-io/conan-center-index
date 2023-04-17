from conans import ConanFile, tools
import os


class TestPackageConan(ConanFile):

    settings = "os", "arch", "compiler", "build_type"

    def test(self):
        if not tools.cross_building(self):
            self.run("genie ninja", run_environment=True, cwd=os.path.join(self.source_folder, "..", "test_package"))
