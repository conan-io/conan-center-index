from conan import ConanFile
from conan.tools.build import can_run
from conans.tools import get_env
import sys
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "arch"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        shutil.copy(os.path.join(self.source_folder, "file_to_check.cpp"),
                    os.path.join(self.build_folder, "file_to_check.cpp"))

        if can_run(self):
            self.run("cppcheck --enable=warning,style,performance --std=c++11 .",
                    cwd=self.source_folder, run_environment=True)
            # On windows we need to explicitly use python to run the python script
            if self.settings.os == 'Windows':
                self.run("{} {} -h".format(sys.executable, get_env("CPPCHECK_HTMLREPORT")))
            else:
                self.run("cppcheck-htmlreport -h", run_environment=True)
