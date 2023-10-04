
import os

from conan import ConanFile
from conan.tools.gnu import AutotoolsToolchain, Autotools, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.files import chdir, get


class gengetoptConan(ConanFile):
    name = "gengetopt"
    package_type = "application"

    # Optional metadata
    license = "<Put the package license here>"
    author = "<Put your name here> <And your email here>"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of {package_name} here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"


    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder,
            strip_root=True)

    def layout(self):
        basic_layout(self, src_folder="src")

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
