from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson
import os

class DpdkTestConan(ConanFile):
    settings = "os", "build_type", "arch", "compiler"
    generators = "PkgConfigDeps", "MesonToolchain", "VirtualRunEnv", "VirtualBuildEnv"
    test_type = "explicit"

    def layout(self):
        basic_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "example")
            self.run(bin_path, env="conanrun")
