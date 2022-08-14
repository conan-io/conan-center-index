from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.cmake import CMake, CMakeDeps, cmake_layout
from conan.tools.gnu import PkgConfig, PkgConfigDeps
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        if self.settings.os != "Windows":
            self.tool_requires("pkgconf/1.7.4")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        if self.settings.os == "Windows":
            cd = CMakeDeps(self)
            cd.generate()
        else:
            pkg = PkgConfigDeps(self)
            pkg.generate()
            ms = VirtualBuildEnv(self)
            ms.generate(scope="build")
            env = Environment()
            env.prepend_path("PKG_CONFIG_PATH", self.generators_folder)
            envvars = env.vars(self, scope="build")
            envvars.save_script("conanbuildenv_pkg_config_path")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")

            pkg_config = PkgConfig(self, "gio-2.0", pkg_config_path=self.generators_folder)
            self.run(f"{pkg_config.variables['gdbus_codegen']} -h", env="conanrun")
