from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi", "pkg_config"

    def build_requirements(self):
        if self.settings.os != "Windows":
            self.build_requires("pkgconf/1.9.3")

    def build(self):
        if self.settings.os != "Windows":
            with tools.environment_append({'PKG_CONFIG_PATH': "."}):
                pkg_config = tools.PkgConfig("gio-2.0")
                self.run(f"{pkg_config.variables['gdbus_codegen']} -h", run_environment=True)

        with tools.environment_append({'PKG_CONFIG_PATH': "."}):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
