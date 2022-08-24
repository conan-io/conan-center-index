from conans import ConanFile, tools
import sys
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "arch"

    def test(self):
        shutil.copy(os.path.join(self.source_folder, "file_to_check.cpp"),
                    os.path.join(self.build_folder, "file_to_check.cpp"))
        if not tools.build.cross_building(self, self.settings):
            self.run("cppcheck --enable=warning,style,performance --std=c++11 .",
                    cwd=self.source_folder, run_environment=True)
            # On windows we need to explicitly use python to run the python script
            if self.settings.os == 'Windows':
                self.run("{} {} -h".format(sys.executable, tools.get_env("CPPCHECK_HTMLREPORT")))
            else:
                self.run("cppcheck-htmlreport -h", run_environment=True)
