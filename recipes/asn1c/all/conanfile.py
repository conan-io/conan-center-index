import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, rmdir, chdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class Asn1cConan(ConanFile):
    name = "asn1c"
    description = "The ASN.1 Compiler"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://lionet.info/asn1c"
    topics = ("asn.1", "compiler")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

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
            self.tool_requires("winflexbison/2.5.24")
        else:
            self.tool_requires("bison/3.8.2")
            self.tool_requires("flex/2.6.4")
        self.tool_requires("libtool/2.4.7")

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("Visual Studio is not supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        tc.configure_args += ["--datarootdir=${prefix}/res"]
        tc.generate()

    def build(self):
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install()
        rmdir(self, os.path.join(self.package_folder, "res", "doc"))
        rmdir(self, os.path.join(self.package_folder, "res", "man"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.resdirs = ["res"]

        # asn1c cannot use environment variables to specify support files path
        # so `SUPPORT_PATH` should be propagated to command line invocation to `-S` argument
        support_path = os.path.join(self.package_folder, "res", "asn1c")
        self.buildenv_info.define_path("SUPPORT_PATH", support_path)

        # TODO: to remove in conan v2
        bin_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_path)
        self.env_info.SUPPORT_PATH = support_path
