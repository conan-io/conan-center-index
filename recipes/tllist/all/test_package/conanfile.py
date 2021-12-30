from conans import ConanFile, Meson, tools
import os


class TestPackageConan(ConanFile):
    generators = "pkg_config"
    settings = "os", "compiler", "build_type", "arch"

    def build_requirements(self):
        self.build_requires("pkgconf/[>=1.7.4]")
        self.build_requires("meson/[>=0.60.0]")
        self.build_requires("ninja/[>=1.10.0]")

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def test(self):
        bin_path = os.path.join(".", "test_package")
        self.run(bin_path, run_environment=True)
