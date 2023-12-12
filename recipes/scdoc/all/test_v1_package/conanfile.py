from conans import ConanFile, tools
import os


class TestPackageConan(ConanFile):

    def test(self):
        if not tools.cross_building(self):
            scd_path = os.path.join(self.source_folder, os.pardir, "test_package", "test_package.1.scd")
            self.run(f"scdoc < {scd_path}", run_environment=True)
