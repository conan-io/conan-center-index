from conans import ConanFile, tools
import os
import shutil
import glob


class TestPackage(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def build(self):
        if self.settings.os == "Windows":
            open(os.path.join(self.source_folder, "WORKSPACE"), "w")
            self.run("bazel build //main:hello-world", run_environment=True)
            for directory in glob.glob(os.path.join(self.source_folder, "bazel-*")):
                shutil.move(directory, self.build_folder)
        else:
            with tools.chdir(self.build_folder):
                open("WORKSPACE", "w")
                self.run("bazel --output_user_root {} build --package_path {} //main:hello-world"
                         .format(self.build_folder, self.source_folder), run_environment=True)

    def test(self):
        self.run("bazel --version", run_environment=True)
        bin_path = os.path.join("bazel-bin", "main", "hello-world")
        self.run(bin_path, run_environment=True)
