import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import copy, save, chdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

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

    def layout(self):
        basic_layout(self)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = AutotoolsToolchain(self)
        tc.generate()

        if is_msvc(self):
            env = Environment()
            automake_conf = self.dependencies.build["automake"].conf_info
            compile_wrapper = unix_path(self, automake_conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, automake_conf.get("user.automake:lib-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            # FIXME: otherwise fails with 'configure: error: could not determine .../automake-1.16/ar-lib "lib -nologo" interface'.
            # env.define("AR", f'{ar_wrapper} "lib -nologo"')
            env.define("AR", unix_path(self, os.path.join(self.build_folder, "build-aux", "ar-lib")))
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
            env.vars(self).save_script("conanbuild_msvc")

    def build(self):
        for src in ["configure.ac", "Makefile.am", "test_package.c"]:
            copy(self, src, src=self.source_folder, dst=self.build_folder)
        for fn in ("COPYING", "NEWS", "INSTALL", "README", "AUTHORS", "ChangeLog"):
            save(self, os.path.join(self.build_folder, fn), "\n")
        # self.run("gnulib-tool --list")
        self.run("gnulib-tool --import getopt-posix")
        autotools = Autotools(self)
        # Can simply do autotools.autoreconf(self.build_folder) in Conan v2
        with chdir(self, self.build_folder):
            self.run("autoreconf -fiv")
        autotools.configure(self.build_folder)
        autotools.make()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")
