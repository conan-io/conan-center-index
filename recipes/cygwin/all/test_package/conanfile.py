from conans import ConanFile, tools
from conans.errors import ConanException

class TestPackage(ConanFile):

    def test(self):
        bash = tools.which("bash.exe")

        if bash:
            self.output.info("using bash.exe from: " + bash)
        else:
            raise ConanException("No instance of bash.exe could be found on %PATH%")

        self.run('cygcheck -c')
        self.run('bash.exe -c ^"uname -a^"')
        self.run('bash.exe -c ^"test -L /etc/networks^"')

