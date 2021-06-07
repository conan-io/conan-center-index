from conans import ConanFile, tools
from conans.errors import ConanException
import os


class TestPackageConan(ConanFile):

    build_requires = (
        "wayland/1.18.0"
    )

    generators = "pkg_config"

    def test(self):
        with tools.environment_append({'PKG_CONFIG_PATH': "."}):
            pkg_config = tools.PkgConfig("wayland-protocols")
            pkg_data_dir = os.path.join(pkg_config.variables["pkgdatadir"], "stable")
            if not os.path.isdir(pkg_data_dir):
                raise ConanException("generated wayland-protocols.pc does not have proper pkgdatadir")
            self.run('wayland-scanner client-header --strict %s /dev/null' % os.path.join(pkg_data_dir, "viewporter", "viewporter.xml"), run_environment=True)
