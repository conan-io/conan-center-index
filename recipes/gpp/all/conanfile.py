
import os

from conan import ConanFile
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.layout import basic_layout
from conan.tools.files import chdir, get

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
    win_bash = True
    
    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"

    def build_requirements(self):
        self.tool_requires("automake/1.16.5")
        self.tool_requires("autoconf/2.71")
        pass
        
    def configure(self):
        # The library is C only
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
    
    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        
    def generate(self):
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
