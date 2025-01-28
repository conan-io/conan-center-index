
import os

from conan import ConanFile
from conan.tools.gnu import AutotoolsToolchain, Autotools, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.files import chdir, get


class GppConan(ConanFile):
    name = "GPP"
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

    def build_requirements(self):
        self.tool_requires("autoconf/2.72")
    
    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version])
        
    def generate(self):
        deps = AutotoolsDeps(self)
        deps.generate()
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
