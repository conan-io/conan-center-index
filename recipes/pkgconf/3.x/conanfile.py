import os

from conan import ConanFile
from conan.tools.files import copy, get, rename, rm, rmdir
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain


required_conan_version = ">=2.4"


class PkgConfConan(ConanFile):
    name = "pkgconf"
    package_type = "application"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("build", "configuration")
    homepage = "https://git.sr.ht/~kaniini/pkgconf"
    license = "pkgconf"
    description = "package compiler and linker metadata toolkit"
    settings = "os", "arch", "compiler", "build_type"
    languages = "C"

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.2 <2]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["default_library"] = "static"
        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder,"licenses"))

        meson = Meson(self)
        meson.install()

        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "include"))
        rename(self, os.path.join(self.package_folder, "share", "aclocal"),
                  os.path.join(self.package_folder, "bin", "aclocal"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        bindir = os.path.join(self.package_folder, "bin")

        exesuffix = ".exe" if self.settings.os == "Windows" else ""
        pkg_config = os.path.join(bindir, "pkgconf" + exesuffix).replace("\\", "/")
        self.buildenv_info.define_path("PKG_CONFIG", pkg_config)

        pkgconf_aclocal = os.path.join(self.package_folder, "bin", "aclocal")
        self.buildenv_info.prepend_path("ACLOCAL_PATH", pkgconf_aclocal)
