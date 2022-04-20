from conans import ConanFile, tools
import os
import shutil
import sys


class TestPackageConan(ConanFile):
    settings = "os", "arch"
    exports_sources = "file_to_check.cpp"

    def test(self):
        shutil.copy(os.path.join(self.source_folder, "file_to_check.cpp"), self.build_folder)
        if not tools.cross_building(self.settings):
            self.run("cppcheck .", run_environment=True)
            # On windows we need to explicitly use python to run the python script
            if self.settings.os == 'Windows':
                self.run("{} {} -h".format(sys.executable, tools.get_env("CPPCHECK_HTMLREPORT")))
            else:
                self.run("cppcheck-htmlreport -h", run_environment=True)
