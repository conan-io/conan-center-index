from conans import ConanFile
import os
import shutil
import glob


class TestPackage(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def build(self):
        slashes = "///" if self.settings.os == "Windows" else "//"
        self.run("bazel build {}main:hello-world".format(slashes,), run_environment=True)
        for directory in glob.glob(os.path.join(self.source_folder, "bazel-*")):
            shutil.move(directory, self.build_folder)

    def test(self):
        self.run("bazel --version", run_environment=True)
        self.run("bazel-bin/main/hello-world", run_environment=True)
