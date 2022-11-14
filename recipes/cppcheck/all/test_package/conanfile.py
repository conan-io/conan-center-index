from conan import ConanFile
from conan.tools.build import cross_building
import os
import sys


class TestPackageConan(ConanFile):
    settings = "os", "arch"
    generators = "VirtualBuildEnv"

    def test(self):
        if not cross_building(self):
            self.run("cppcheck --enable=warning,style,performance --std=c++11 .",
                    cwd=self.source_folder, run_environment=True)
            if self.settings.os == 'Windows':
                # Unable to work with Environment variable CPPCHECK_HTML_REPORT
                #elf.run(f"{sys.executable} %CPPCHECK_HTML_REPORT% -h", run_environment=True)
                pass
            else:
                self.run("cppcheck-htmlreport -h", run_environment=True)
