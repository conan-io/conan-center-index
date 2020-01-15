import os
from conans import ConanFile, tools


class TestPackageConan(ConanFile):

    def test(self):
        self.output.info("Node version:")
        self.run("node --version", run_environment=True)