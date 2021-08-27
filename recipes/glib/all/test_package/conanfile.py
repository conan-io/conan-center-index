from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package", "pkg_config"

    def build(self):
        if self.settings.os != "Windows":
            with tools.environment_append({'PKG_CONFIG_PATH': "."}):
                pkg_config = tools.PkgConfig("gio-2.0")
                self.run("%s -h" % pkg_config.variables["gdbus_codegen"], run_environment=True)

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
