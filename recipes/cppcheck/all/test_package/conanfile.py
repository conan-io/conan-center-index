from conans import ConanFile, tools
import sys


class TestPackageConan(ConanFile):
    settings = "os", "arch"

    def test(self):
        if not tools.cross_building(self):
            self.run("cppcheck --enable=warning,style,performance --std=c++11 ./file_to_check.cpp",
                    cwd=self.source_folder, run_environment=True)
            # On windows we need to explicitly use python to run the python script
            if self.settings.os == 'Windows':
                self.run("{} {} -h".format(sys.executable, tools.get_env("CPPCHECK_HTMLREPORT")))
            else:
                self.run("cppcheck-htmlreport -h", run_environment=True)
