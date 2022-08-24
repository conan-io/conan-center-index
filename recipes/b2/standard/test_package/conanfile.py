from conan import ConanFile, tools$
import os


class TestPackgeConan(ConanFile):
    settings = "os", "arch"

    def test(self):
        self.run("b2 -v", run_environment=True)
