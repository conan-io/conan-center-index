import os

from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.cmake import CMake
from conan.tools.gnu import PkgConfig
from conan.tools.layout import cmake_layout

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps", "PkgConfigDeps", "VirtualBuildEnv", "VirtualRunEnv"

    def layout(self):
        cmake_layout(self)

    def build(self):
        if self.settings.os != "Windows":
            pkg_config = PkgConfig(self, "gio-2.0", self.generators_folder)
            gdbus_codegen = pkg_config.variables["gdbus_codegen"]
            self.run(f"{gdbus_codegen} -h", env="conanrun")
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            cmd = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(cmd, env="conanrun")
