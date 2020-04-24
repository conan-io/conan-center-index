from conans import CMake, ConanFile, tools
from conans.errors import ConanException
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            self.run(os.path.join("bin", "test_package"), run_environment=True)

            if not os.environ["PKG_CONFIG"].startswith(self.deps_cpp_info["pkgconf"].rootpath):
                raise ConanException("PKG_CONFIG variable incorrect")

            pkgconf_path = tools.which("pkgconf").replace("\\", "/")
            if not pkgconf_path.startswith(self.deps_cpp_info["pkgconf"].rootpath):
                raise ConanException("pkgconf executable not found")

            with tools.environment_append({"PKG_CONFIG_PATH": self.source_folder}):
                self.run("{} libexample1 --libs".format(os.environ["PKG_CONFIG"]), run_environment=True)
                self.run("{} libexample1 --cflags".format(os.environ["PKG_CONFIG"]), run_environment=True)
