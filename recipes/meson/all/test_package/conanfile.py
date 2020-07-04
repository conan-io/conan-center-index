from conans import ConanFile, Meson, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "pkg_config"

    @property
    def _prefix(self):
        return os.path.join(self.build_folder, "prefix")

    def build(self):
        self.package_folder = self._prefix
        meson = Meson(self)
        meson.configure(build_folder="build")
        meson.build()
        meson.install()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join(self._prefix, "bin", "test_package")
            self.run(bin_path, run_environment=True)

        self.run("meson --version")

