import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import copy, save, chdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.microsoft import is_msvc, unix_path


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"
    win_bash = True  # Needed in Conan v1 to avoid "Cannot wrap command with different envs."

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        self.tool_requires("automake/1.16.5")
        self.tool_requires("libtool/2.4.7")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = AutotoolsToolchain(self)
        tc.generate()

        if is_msvc(self):
            env = Environment()
            automake_conf = self.dependencies.build["automake"].conf_info
            compile_wrapper = unix_path(self, automake_conf.get("user.automake:compile-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            # ar-lib wrapper is added automatically by ./configure, no need to set AR
            env.vars(self).save_script("conanbuild_msvc")

    def build(self):
        for src in ["configure.ac", "Makefile.am", "test_package.c"]:
            copy(self, src, src=self.source_folder, dst=self.build_folder)
        for fn in ("COPYING", "NEWS", "INSTALL", "README", "AUTHORS", "ChangeLog"):
            save(self, os.path.join(self.build_folder, fn), "\n")
        self.run("gnulib-tool --list")
        self.run("gnulib-tool --import getopt-posix", env="conanbuild")
        with chdir(self, self.build_folder):
            autotools = Autotools(self)
            if self._settings_build.os == "Windows":
                # Disable m4 from Conan, which is not able to run shell commands with syscmd()
                os.environ["M4"] = ""
            # autotools.autoreconf() does not have build_script_folder param in Conan v1, so using .run()
            self.run("autoreconf -fiv")
            autotools.configure(self.build_folder)
            autotools.make()

    def test(self):
        if can_run(self):
            bin_path = unix_path(self, os.path.join(self.build_folder, "test_package"))
            self.run(bin_path, env="conanrun")
