from conans import ConanFile, tools
from conans.errors import ConanException
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def test(self):
        if not tools.cross_building(self.settings):
            if not os.environ["PKG_CONFIG"].startswith(self.deps_cpp_info["pkgconf"].rootpath):
                raise ConanException("PKG_CONFIG variable incorrect")

            pkgconf_path = tools.which("pkgconf").replace("\\", "/")
            if not pkgconf_path.startswith(self.deps_cpp_info["pkgconf"].rootpath):
                raise ConanException("pkgconf executable not found")

            with tools.environment_append({"PKG_CONFIG_PATH": self.source_folder}):
                self.run("{} libexample1 --libs".format(os.environ["PKG_CONFIG"]))
                self.run("{} libexample1 --cflags".format(os.environ["PKG_CONFIG"]))
