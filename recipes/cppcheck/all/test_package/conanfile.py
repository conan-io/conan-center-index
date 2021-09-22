from conans import ConanFile, tools


class TestPackageConan(ConanFile):
    settings = "os", "arch"

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("cppcheck --version", run_environment=True)
            # On windows we need to explicitly use python to run the python script
            if self.settings.os == 'Windows' and tools.which("python3"):
                self.run("python3 $CPPCHECK_HTMLREPORT -h", run_environment=True)
            else:
                self.run("cppcheck-htmlreport -h", run_environment=True)
