from conan import ConanFile
from conan.tools.build import can_run
import sys


class TestPackageConan(ConanFile):
    settings = "os", "arch"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def test(self):
        if not can_run(self):
            self.run("cppcheck --enable=warning,style,performance --std=c++11 .",
                     cwd=self.source_folder, env="conanbuild")
            if self.settings.os == "Windows":
                # Unable to work with Environment variable CPPCHECK_HTML_REPORT
                self.run(f"{sys.executable} %CPPCHECK_HTML_REPORT% -h", run_environment=True)
            else:
                self.run("cppcheck-htmlreport -h", run_environment=True)
