from conans import ConanFile, tools
import sys


class TestPackageConan(ConanFile):
    settings = "os", "arch"

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("cppcheck --version", run_environment=True)
            # On windows we need to explicitly use python to run the python script
            if self.settings.os == 'Windows':
                self.run("{} {} -h".format(sys.executable, tools.get_env("CPPCHECK_HTMLREPORT")))
            else:
                self.run("cppcheck-htmlreport -h", run_environment=True)
