from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi", "pkg_config"

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.0.3")

    def build(self):
        if self.settings.os != 'Windows':
            with tools.environment_append({'PKG_CONFIG_PATH': "."}):
                pkg_config = tools.PkgConfig("gobject-introspection-1.0")
                for tool in ["g_ir_compiler", "g_ir_generate", "g_ir_scanner"]:
                    self.run('%s --version' % pkg_config.variables[tool], run_environment=True)
                self.run('g-ir-annotation-tool --version', run_environment=True)
                self.run('g-ir-inspect -h', run_environment=True)

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_basic")
            self.run(bin_path, run_environment=True)

