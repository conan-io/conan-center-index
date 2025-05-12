import os.path

from conan import ConanFile
from conan.tools.build import can_run


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        assert os.path.exists(os.path.join(self.dependencies[self.tested_reference_str].cpp_info.bindir, "7za"))
        if can_run(self):
            self.run("7za", env="conanrun")
