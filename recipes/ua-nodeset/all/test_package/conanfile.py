import os

from conan import ConanFile
from conan.tools.files import load, save


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def layout(self):
        pass

    def generate(self):
        nodeset_dir = self.dependencies["ua-nodeset"].conf_info.get("user.ua-nodeset:nodeset_dir")
        save(self, "nodeset_dir", nodeset_dir)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        nodeset_dir = load(self, "nodeset_dir")
        test_path = os.path.join(nodeset_dir, "PLCopen")
        assert os.path.exists(test_path)
