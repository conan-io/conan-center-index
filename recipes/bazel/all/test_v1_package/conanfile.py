from conan.tools.build import can_run
from conans import ConanFile


class TestPackageV1Conan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def test(self):
        if can_run(self):
            # self.run checks the command exit code
            # the tool must be available on PATH, which is configured by self.env_info.PATH
            self.run("bazel --version", run_environment=True)
