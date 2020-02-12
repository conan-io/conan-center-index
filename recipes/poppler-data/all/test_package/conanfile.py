from conans import ConanFile
import os


class TestPackageConan(ConanFile):

    def test(self):
        os.path.isdir(self.deps_user_info["poppler-data"].datadir)
