from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import copy
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"
    win_bash = True

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def layout(self):
        basic_layout(self)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)
        if self._settings_build.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", check_type=str):
            self.tool_requires("msys2/cci.latest")

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = AutotoolsToolchain(self)
        tc.generate()
        if is_msvc(self):
            env = Environment()
            env.define("CC", "cl -nologo")
            env.define("CXX", "cl -nologo")
            env.vars(self).save_script("conanbuild_msvc")

    def build(self):
        for src in ("configure.ac", "config.h.in", "Makefile.in", "test_package_c.c", "test_package_cpp.cpp"):
            copy(self, src, self.source_folder, self.build_folder)
        self.run("autoconf --verbose")
        autotools = Autotools(self)
        autotools.configure(build_script_folder=self.build_folder)
        autotools.make()

    def test(self):
        self.win_bash = None
        if can_run(self):
            bin_path = os.path.join(self.build_folder, "test_package")
            self.run(bin_path, env="conanrun")
