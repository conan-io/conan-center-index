from conans import ConanFile
import os


class TestPackageConan(ConanFile):

    def test(self):
        if not os.path.isdir(self.deps_user_info["poppler-data"].datadir):
            raise AssertionError("datadir is not a directory")
