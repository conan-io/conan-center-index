from conan import ConanFile
from conan.tools.build import can_run

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        if can_run(self):
            extension = ".exe" if self.settings.os == "Windows" else ""
            self.run(f"m4{extension} --version", env="conanrun")
