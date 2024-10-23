from conan import ConanFile, conan_version
from conan.tools.gnu import Autotools
from conan.tools.layout import basic_layout
from conan.tools.files import get, mkdir, apply_conandata_patches, rmdir, copy
from conan.tools.scm import Version

import pathlib


class gengetoptConan(ConanFile):
    name = "gengetopt"
    package_type = "application"

    # Optional metadata
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/gengetopt/gengetopt.html"
    description = "A tool to write command line option parsing code for C programs."
    topics = ("gnu", "generator", "parsing", "command-line")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "patches/*.patch"
    generators = "AutotoolsDeps", "AutotoolsToolchain", "VirtualRunEnv"

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.tool_requires("msys2/cci.latest")
            self.tool_requires("winflexbison/2.5.25")
        else:
            self.tool_requires("flex/2.6.4")
            self.tool_requires("bison/3.8.2")
        self.tool_requires("automake/1.16.5")
        self.tool_requires("autoconf/2.71")
        self.tool_requires("libtool/2.4.7")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder,
            strip_root=True)

    def layout(self):
        basic_layout(self, src_folder="src")

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
        mkdir(self, lic_path)
        copy(self, "COPYING", self.source_folder, lic_path)
        copy(self, "LICENSE", self.source_folder, lic_path)

        share_path = pathlib.Path(self.package_folder) / "share"
        rmdir(self, share_path)


    def package_info(self):
        self.cpp_info.includedirs.clear()
        self.cpp_info.libdirs.clear()

        if Version(conan_version).major < 2:
            binpath = pathlib.Path(self.package_folder) / "bin"
            self.env_info.PATH.append(str(binpath))


    def package_id(self):
        del self.info.settings.compiler
