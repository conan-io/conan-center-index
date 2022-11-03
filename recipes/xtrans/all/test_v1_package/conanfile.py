from conans import ConanFile
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "pkg_config"

    def build(self):
        pass

    def test(self):
        self.run("pkg-config --validate ./xtrans.pc")
