from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.files import copy
from conan.tools.env import VirtualBuildEnv
from conan.tools.microsoft import is_msvc
from conan.tools.build import can_run
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def export_sources(self):
        copy(self, "Imakefile", self.recipe_folder, self.export_folder)
        copy(self, "test_package.c", self.recipe_folder, self.export_folder)

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def layout(self):
        basic_layout(self)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)
        self.tool_requires("imake/1.0.8")
        if not self.conf_info.get("tools.gnu:make_program", check_type=str):
            self.tool_requires("make/4.3")

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        env = tc.environment()
        if is_msvc(self):
            env.define("CC", "cl -nologo")
        tc.generate()

    def build(self):
        self.run("imake -DUseInstalled -I{}".format(self.deps_user_info["xorg-cf-files"].CONFIG_PATH), env="conanbuild")
        autotools = Autotools(self)
        autotools.make(target="test_package")

    def test(self):
        if can_run(self):
            bindir = self.cpp_info.bindirs[0]
            self.run(os.path.join(bindir, "test_package"), env="conanrun")
