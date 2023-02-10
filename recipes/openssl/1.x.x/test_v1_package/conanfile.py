from conans import CMake, ConanFile, tools
from conans.errors import ConanException
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package"

    def _openssl_option(self, name, default):
        try:
            return getattr(self.options["openssl"], name, default)
        except (AttributeError, ConanException):
            return default

    def build(self):
        cmake = CMake(self)
        cmake.definitions["OPENSSL_WITH_ZLIB"] = not self._openssl_option("no_zlib", True)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
