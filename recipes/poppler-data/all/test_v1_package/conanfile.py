from conans import ConanFile
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def test(self):
        if not os.path.isdir(self.deps_user_info["poppler-data"].datadir):
            raise AssertionError("datadir is not a directory")
