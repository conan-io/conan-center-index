from conans import ConanFile, tools
import os


class TestPackgeConan(ConanFile):
    settings = "os", "arch"

    def test(self):
        tools.save(
            "jamroot.jam",
            'ECHO "info:" Success loading project jamroot.jam file. ;')
        self.run("b2 --debug-configuration", run_environment=True)
