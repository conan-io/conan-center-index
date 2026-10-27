
import os

from conan import ConanFile
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.layout import basic_layout
from conan.tools.files import chdir, get
from conan.tools.env import VirtualBuildEnv

class GppConan(ConanFile):
    name = "gpp"
    version = "2.28"
    package_type = "application"

    # Optional metadata
    license = "GPL-3.0"
    author = "Dan Weatherill <dan.weatherill@cantab.net>"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://logological.org/gpp"
    description = "A generic preprocessor"
    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    win_bash = True

    def build_requirements(self):
        self.tool_requires("automake/1.16.5")
        self.tool_requires("autoconf/2.71")

        if self.settings_build.os == "Windows":
            self.win_bash = True
            self.tool_requires("msys2/cci.latest")
            self.tool_requires("mingw-builds/14.2.0")

    def requirements(self):
        self.requires("msys2/cci.latest")

    def configure(self):
        # The library is C only
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def package_id(self):
        del self.info.settings.arch
        del self.info.settings.compiler
        del self.info.settings.build_type

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        at_toolchain = AutotoolsToolchain(self)
        at_toolchain.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.autoreconf()        
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install()
