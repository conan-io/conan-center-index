from conans import ConanFile, Meson
from conan.tools.build import cross_building
import os


# legacy validation with Conan 1.x
class TestPackageV1Conan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "pkg_config"

    def build_requirements(self):
        self.build_requires("meson/0.63.3")
        self.build_requires("pkgconf/1.9.3")

    def build(self):
        meson = Meson(self)
        meson.configure(build_folder="bin", source_folder="../test_package")
        meson.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
