from conans import ConanFile, Meson, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "pkg_config"

    def build(self):
        if not tools.build.cross_building(self, self):
            with tools.environment_append(tools.RunEnvironment(self).vars):
                meson = Meson(self)
                meson.configure(build_folder="build")
                meson.build()

    def test(self):
        if not tools.build.cross_building(self, self):
            bin_path = os.path.join("build", "test_package")
            self.run(bin_path, run_environment=True)

            self.run("meson --version", run_environment=True)
