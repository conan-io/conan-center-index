from conan import ConanFile
from conan.tools.files import save, load
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        save(self, "hwdata_pkg_dir", self.dependencies[self.tested_reference_str].package_folder)

    def test(self):
        pkg_dir = load(self, "hwdata_pkg_dir")
        assert os.path.isfile(os.path.join(pkg_dir, "res", "hwdata", "usb.ids"))
