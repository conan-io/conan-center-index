import os

from conan import ConanFile
from conan.tools.files import chdir, load


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        tar_bin = self.dependencies.build["tar"].conf_info.get("user.tar:tar")
        with chdir(self, self.source_folder):
            test_tar = os.path.join(self.build_folder, "test.tar.gz")
            self.run(f"{tar_bin} -czf {test_tar} conanfile.py")
        assert os.path.isfile("test.tar.gz")
        self.run(f"{tar_bin} -tf test.tar.gz")
        self.run(f"{tar_bin} -xf test.tar.gz")
        f1 = load(self, os.path.join(self.source_folder, "conanfile.py"))
        f2 = load(self, os.path.join(self.build_folder, "conanfile.py"))
        assert f1 == f2
