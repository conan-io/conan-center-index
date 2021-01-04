from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def test(self):
        with tools.chdir(self.source_folder), tools.remove_from_path("make"):
            env_build = AutoToolsBuildEnvironment(self)
            env_build.make(args=["love"])
