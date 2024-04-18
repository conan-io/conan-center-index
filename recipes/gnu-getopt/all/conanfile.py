import os

from conan import ConanFile
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import copy, get
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path

required_conan_version = ">=1.54.0"


class GnuGetoptConan(ConanFile):
    name = "gnu-getopt"
    description = "GNU getopt(1) command-line utility"
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://frodo.looijaard.name/project/getopt"
    topics = ("gnu", "getopt", "utility", "command-line", "parsing")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        # liblastlog support requires sqlite3
        tc.configure_args.append("--disable-liblastlog2")
        tc.generate()

        if is_msvc(self):
            env = Environment()
            automake_conf = self.dependencies.build["automake"].conf_info
            compile_wrapper = unix_path(self, automake_conf.get("user.automake:compile-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.vars(self).save_script("conanbuild_msvc")

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        target = "getopt.exe" if self.settings.os == "Windows" else "getopt"
        autotools.make(target)

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "getopt*", self.build_folder, os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.frameworkdirs = []
