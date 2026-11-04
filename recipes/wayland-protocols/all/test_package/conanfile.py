from conan import ConanFile
from conan.tools.layout import basic_layout
import os
import glob


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        basic_layout(self)

    def test(self):
        wayland_folder = os.path.join(self.dependencies[self.tested_reference_str].package_folder, "res", "wayland-protocols")
        assert os.path.isdir(wayland_folder)
        xml_files = glob.glob(os.path.join(wayland_folder, "**", "*.xml"), recursive=True)
        assert len(xml_files) > 0
