from pathlib import Path

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str, run=True)

    def test(self):
        if can_run(self):
            self.run("cargo-cbuild --version", env="conanrun")
        else:
            ext = ".exe" if self.settings.os == "Windows" else ""
            assert Path(self.dependencies["cargo-c"].package_folder, "bin", "cargo-cbuild" + ext).exists()
