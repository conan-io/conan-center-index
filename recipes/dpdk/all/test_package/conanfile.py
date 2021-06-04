from conans import ConanFile, Meson, tools
import os


class DpdkTestConan(ConanFile):
    settings = "os", "build_type", "arch", "compiler"
    generators = "pkg_config"

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def test(self):
        if not tools.cross_building(self):
            self.run("example", run_environment=True)
