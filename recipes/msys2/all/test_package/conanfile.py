from conan import ConanFile, tools
from conans.errors import ConanException
from io import StringIO

class TestPackage(ConanFile):
    
    def build(self):
        pass # nothing to do, skip hook warning

    def test(self):
        bash = tools.which("bash.exe")
        
        if bash:
            self.output.info("using bash.exe from: " + bash)
        else:
            raise ConanException("No instance of bash.exe could be found on %PATH%")
        
        self.run('bash.exe -c ^"make --version^"')
        self.run('bash.exe -c ^"! test -f /bin/link^"')
        self.run('bash.exe -c ^"! test -f /usr/bin/link^"')

        secret_value = "SECRET_CONAN_PKG_VARIABLE"
        with tools.environment_append({"PKG_CONFIG_PATH": secret_value}):
            output = StringIO()
            self.run('bash.exe -c "echo $PKG_CONFIG_PATH"', output=output)
            print(output.getvalue())
            assert secret_value in output.getvalue()
