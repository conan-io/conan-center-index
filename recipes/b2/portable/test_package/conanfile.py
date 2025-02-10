from pathlib import Path

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.layout import basic_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        basic_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str, run=True)

    def test(self):
        if can_run(self):
            self.run("b2 -v", env="conanrun")
        else:
            suffix = ".exe" if self.settings.os == "Windows" else ""
            assert Path(self.dependencies["b2"].package_folder, "bin", f"b2{suffix}").is_file()
