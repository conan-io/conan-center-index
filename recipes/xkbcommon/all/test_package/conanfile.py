from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "pkg_config"

    def build(self):
        with tools.environment_append({'PKG_CONFIG_PATH': '.'}):
            self.output.info("xkbcommon libs: %s" % " ".join(tools.PkgConfig("xkbcommon").libs_only_l))
            self.output.info("xkbcommon-x11 libs: %s" % " ".join(tools.PkgConfig("xkbcommon-x11").libs_only_l))
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
