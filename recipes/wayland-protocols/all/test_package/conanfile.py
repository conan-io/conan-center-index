from conans import ConanFile, Meson, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "pkg_config"

    def build_requirements(self):
        self.build_requires("wayland/1.19.0")
        self.build_requires("meson/0.59.1")

    def requirements(self):
        self.requires("wayland/1.19.0")

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def test(self):
        if not tools.cross_building(self.settings):
            self.run(os.path.join(".", "test_package"), run_environment=True)
