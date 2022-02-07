from conans import ConanFile, tools
import os


class TestPackageConan(ConanFile):

    def test(self):
        if not tools.cross_building(self):
            self.run(
                f"scdoc < {os.path.join(self.source_folder,'test_package.1.scd')}", run_environment=True)
