import os

from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.cmake import CMake
from conan.tools.gnu import PkgConfig
from conan.tools.layout import cmake_layout


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps", "PkgConfigDeps", "VirtualRunEnv"

    def layout(self):
        cmake_layout(self)

    def build(self):
        if not cross_building(self):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()
            pkg_config = PkgConfig(self, "wayland-scanner", self.generators_folder)
            self.run('%s --version' % pkg_config.variables["wayland_scanner"], env="conanrun")

    def test(self):
        if not cross_building(self):
            cmd = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(cmd, env="conanrun")
