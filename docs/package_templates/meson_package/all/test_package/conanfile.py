from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson
import os


# It will become the standard on Conan 2.x
class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "PkgConfigDeps", "MesonToolchain", "VirtualRunEnv", "VirtualBuildEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.tool_requires("meson/0.63.3")
        self.tool_requires("pkgconf/1.9.3")
        if not self.conf.get("tools.meson.mesontoolchain:backend", default=False, check_type=str):
            self.tools_requires("ninja/1.11.1")

    def layout(self):
        basic_layout(self)

    def build(self):
        cmake = Meson(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
