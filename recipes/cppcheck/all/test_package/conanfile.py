from conan import ConanFile
from conan.tools.build import can_run


class TestPackageConan(ConanFile):
    settings = "os", "arch"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        if can_run(self):
            self.run("cppcheck --enable=warning,style,performance --std=c++11 .",
                     cwd=self.source_folder)
            if self.settings.os == "Windows":
                self.run("set CPPCHECK_HTMLREPORT")
            else:
                self.run("which cppcheck-htmlreport")
