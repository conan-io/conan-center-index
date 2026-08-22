import os
from conan import ConanFile


class TestPackageConan(ConanFile):

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        assert os.path.exists(os.path.join(self.dependencies[self.tested_reference_str].cpp_info.bindir, "gas-preprocessor.pl"))
