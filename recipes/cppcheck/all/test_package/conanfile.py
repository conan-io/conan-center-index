from conan import ConanFile
from conan.tools.build import can_run
import sys


class TestPackageConan(ConanFile):
    settings = "os", "arch"
    generators = "VirtualRunEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        if can_run(self):
            self.run("cppcheck --enable=warning,style,performance --std=c++11 .",
                     cwd=self.source_folder, run_environment=True)
            if self.settings.os == "Windows":
                self.run(f"{sys.executable} %CPPCHECK_HTMLREPORT% -h", run_environment=True)
            else:
                self.run("cppcheck-htmlreport -h", run_environment=True)
