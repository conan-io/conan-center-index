from conans import ConanFile
import os


class TestPackage(ConanFile):

    def test(self):
        self.run("ninja --version", run_environment=True)
