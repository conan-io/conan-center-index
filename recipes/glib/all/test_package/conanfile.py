from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeDeps, cmake_layout
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.gnu import PkgConfig, PkgConfigDeps
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        if self.settings.os != "Windows":
            self.tool_requires("pkgconf/1.9.3")

    def generate(self):
        if self.settings.os == "Windows":
            deps = CMakeDeps(self)
            deps.generate()
        else:
            env = VirtualBuildEnv(self)
            env.generate()
            pkg = PkgConfigDeps(self)
            pkg.generate()
            # TODO: to remove when properly handled by conan (see https://github.com/conan-io/conan/issues/11962)
            env = Environment()
            env.prepend_path("PKG_CONFIG_PATH", self.generators_folder)
            env.vars(self).save_script("conanbuildenv_pkg_config_path")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")

            if self.settings.os != "Windows":
                pkg_config = PkgConfig(self, "gio-2.0", pkg_config_path=self.generators_folder)
                gdbus_codegen = pkg_config.variables["gdbus_codegen"]
                self.run(f"{gdbus_codegen} -h", env="conanrun")
