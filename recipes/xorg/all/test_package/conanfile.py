import os

from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.cmake import CMake
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import cmake_layout


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps", "VirtualBuildEnv", "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        pkg_config_deps = PkgConfigDeps(self)
        pkg_config_deps.generate()
        pkg_config = self.conf_info.get("tools.gnu:pkg_config", default="pkg-config")
        uuid_pkg_config_file = os.path.join(self.generators_folder, "uuid.pc")
        self.run(f"{pkg_config} --validate {uuid_pkg_config_file}")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            cmd = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(cmd, env="conanrun")
