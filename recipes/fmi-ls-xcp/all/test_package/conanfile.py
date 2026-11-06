import os
from conan import ConanFile


class TestPackageConan(ConanFile):
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        res_dir = os.path.join(self.dependencies["fmi-ls-xcp"].package_folder, "res")
        xsd_file = os.path.join(res_dir, "fmi3LayeredStandardXcpManifest.xsd")
        assert os.path.isfile(xsd_file), f"Expected XSD file not found at: {xsd_file}"
