from conans import ConanFile, tools
from conans.errors import ConanException


class TestPackageConan(ConanFile):

    def test(self):
        pwsh = tools.which("pwsh")
        if pwsh:
            self.output.info("using pwsh from: " + pwsh)
        else:
            raise ConanException("No instance of pwsh could be found in PATH")

        self.run("pwsh --help")
