from conans import ConanFile
import os


class TestPackage(ConanFile):

    def test(self):
        self.run("yasm --help", run_environment=True)
