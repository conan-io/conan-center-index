from conans import ConanFile
import os


class TestPackage(ConanFile):

    def test(self):
        self.run("gn --version", run_environment=True)
