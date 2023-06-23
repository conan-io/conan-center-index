import os

from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.files import copy
from conan.tools.env import VirtualBuildEnv
from conan.tools.microsoft import is_msvc
from conan.tools.build import can_run


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "Imakefile", "test_package.c"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)
        self.tool_requires("imake/1.0.8")
        if not self.conf_info.get("tools.gnu:make_program", check_type=str):
            self.tool_requires("make/4.3")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def layout(self):
        basic_layout(self)

    def generate(self):
        tc = AutotoolsToolchain(self)
        env = tc.environment()
        if is_msvc(self):
            env.define("CC", "cl -nologo")
        tc.generate()

        buildenv = VirtualBuildEnv(self)
        buildenv.generate()

    def build(self):
        for src in self.exports_sources:
            copy(self, src, self.source_folder, self.build_folder)

        config_path = self.conf.get("user.xorg-cf-files:config-path")
        self.run(f"imake -DUseInstalled -I{config_path}", env="conanbuild")
        autotools = Autotools(self)
        autotools.make(target="test_package")

    def test(self):
        if can_run(self):
            self.run(os.path.join(".", "test_package"), env="conanrun")
