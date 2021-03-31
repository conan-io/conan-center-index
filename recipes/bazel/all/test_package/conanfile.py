from conans import ConanFile, tools
import os


class TestPackage(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def build(self):
        with tools.chdir(self.build_folder):
            open("WORKSPACE", "w")
            self.run("bazel --output_user_root {} build -s --package_path {} //main:hello-world"
                     .format(self.build_folder, self.source_folder), run_environment=True)

    def test(self):
        self.run("bazel --version", run_environment=True)
        bin_path = os.path.join("bazel-bin", "main", "hello-world")
        self.run(bin_path, run_environment=True)
