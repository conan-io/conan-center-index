from conans import ConanFile, tools

import os


class TestPackageConan(ConanFile):

    def test(self):
        pkgconf_path = tools.which("pkgconf").replace("\\", "/")
        assert pkgconf_path.startswith(self.deps_cpp_info["pkgconf"].rootpath)

        assert os.environ["PKG_CONFIG"].startswith(self.deps_cpp_info["pkgconf"].rootpath)

        with tools.environment_append({"PKG_CONFIG_PATH": self.source_folder}):
            self.run("{} libexample1 --libs".format(os.environ["PKG_CONFIG"]))
            self.run("{} libexample1 --cflags".format(os.environ["PKG_CONFIG"]))
