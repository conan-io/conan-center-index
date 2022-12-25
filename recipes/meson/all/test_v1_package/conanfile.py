from conans import ConanFile, Meson, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def build_requirements(self):
        self.build_requires(self.tested_reference_str)

    def build(self):
        if not tools.cross_building(self):
            meson = Meson(self)
            meson.configure(build_folder="build")
            meson.build()

    def test(self):
        self.run("meson --version")
        if not tools.cross_building(self):
            bin_path = os.path.join("build", "test_package")
            self.run(bin_path, run_environment=True)
