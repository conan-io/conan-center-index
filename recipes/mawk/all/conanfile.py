from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, rmdir, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
import os


required_conan_version = ">=1.54.0"


class PackageConan(ConanFile):
    name = "mawk"
    description = "mawk is an interpreter for the AWK Programming Language."
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://invisible-island.net/mawk/mawk.html"
    topics = ("awk", "app", "interpreter", "programming-language")
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        # INFO: The certificate of the website is expired/invalid
        get(self, **self.conan_data["sources"][self.version], strip_root=True, verify=False)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")
        tc = AutotoolsToolchain(self)
        tc.generate()

        if is_msvc(self):
            env = Environment()
            env.define("CC", "cl -nologo")
            env.define("CXX", "cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", "lib -nologo")
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
            # INFO: It's not able to find lib math on Windows without passing its path.
            env.define("MATHLIB", os.path.join(self.dependencies.build["msys2"].package_folder, "usr", "lib", "libm.a"))
            env.vars(self).save_script("conanbuild_msvc")

    def _patch_sources(self):
        if is_msvc(self):
            # INFO: MAWK_RAND_MAX is not defined when building on Windows. Use system RAND_MAX instead.
            replace_in_file(self, os.path.join(self.source_folder, 'bi_funct.c'), 'MAWK_RAND_MAX', 'RAND_MAX')

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, pattern="COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        # TODO: Legacy, to be removed on Conan 2.0
        bin_folder = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_folder)
