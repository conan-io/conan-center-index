from conans import ConanFile, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def test(self):
        tar_bin = self.deps_user_info["tar"].tar
        if not tools.cross_building(self):
            with tools.chdir(self.source_folder):
                test_tar = os.path.join(self.build_folder, "test.tar.gz")
                self.run("{} -czf {} conanfile.py".format(tar_bin, test_tar), run_environment=True)
            assert os.path.isfile("test.tar.gz")
            self.run("{} -tf test.tar.gz".format(tar_bin), run_environment=True)
            self.run("{} -xf test.tar.gz".format(tar_bin), run_environment=True)
            assert tools.load(os.path.join(self.source_folder, "conanfile.py")) == tools.load(os.path.join(self.build_folder, "conanfile.py"))
