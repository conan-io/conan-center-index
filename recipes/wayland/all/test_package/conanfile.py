from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "pkg_config"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        if not tools.cross_building(self, skip_x64_x86=True):
            with tools.environment_append({'PKG_CONFIG_PATH': "."}):
                pkg_config = tools.PkgConfig("wayland-scanner")
                self.run('%s --version' % pkg_config.variables["wayland_scanner"], run_environment=True)

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)

