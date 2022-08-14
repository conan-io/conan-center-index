import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake
from conan.tools.env import Environment
from conan.tools.cmake import cmake_layout

required_conan_version = ">=1.38.0"


class LibcapTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "PkgConfigDeps", "VirtualBuildEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.tool_requires("pkgconf/1.7.4")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        env = Environment()
        env.prepend_path("PKG_CONFIG_PATH", self.generators_folder)
        envvars = env.vars(self)
        envvars.save_script("pkg_config")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "example")
            self.run(bin_path, env="conanrun")
