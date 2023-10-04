from conan import ConanFile
from conan.tools.gnu import AutotoolsToolchain, Autotools, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.files import get, mkdir, apply_conandata_patches

import pathlib


class gengetoptConan(ConanFile):
    name = "gengetopt"
    package_type = "application"

    # Optional metadata
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A tool to write command line option parsing code for C programs."
    topics = ("gnu", "generator", "parsing", "command-line")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"

    def build_requirements(self):
        self.tool_requires("gengen/1.4.2")
        self.tool_requires("flex/2.6.4")
        self.tool_requires("bison/3.8.2")

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
        apply_conandata_patches(self)

        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install()

        lic_path = pathlib.Path(self.package_folder) / "licenses"
        mkdir(lic_path)
        copy(self, "COPYING", self.source_folder, lic_path)
        copy(self, "LICENSE", self.source_folder, lic_path)
