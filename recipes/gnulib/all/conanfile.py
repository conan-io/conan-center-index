import os

from conan import ConanFile
from conan.tools.files import copy, rmdir
from conan.tools.layout import basic_layout
from conan.tools.scm import Git

required_conan_version = ">=1.52.0"


class GnuLibConanFile(ConanFile):
    name = "gnulib"
    description = "Gnulib is a central location for common GNU code, intended to be shared among GNU packages."
    license = ("GPL-3.0-or-later", "LGPL-3.0-or-later", "Public-domain")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/gnulib/"
    topics = ("library", "gnu")

    package_type = "build-scripts"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        git = Git(self)
        sources = self.conan_data["sources"][self.version]
        # fetch_commit() landed in Conan 1.59. Older clients allowed by
        # required_conan_version still check out this exact commit.
        if hasattr(git, "fetch_commit"):
            git.fetch_commit(url=sources["url"], commit=sources["commit"])
        else:
            git.clone(url=sources["url"], target=".")
            git.checkout(commit=sources["commit"])
        rmdir(self, os.path.join(self.source_folder, ".git"))

    def package(self):
        copy(self, "COPYING",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*",
             dst=os.path.join(self.package_folder, "bin"),
             src=self.source_folder)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        # Set GNULIB_SRCDIR for the standard ./bootstrap script from build-aux
        # https://github.com/digitalocean/gnulib/blob/master/build-aux/bootstrap#L58-L62
        self.buildenv_info.define_path("GNULIB_SRCDIR", os.path.join(self.package_folder, "bin"))

        # TODO: Legacy, to be removed on Conan 2.0
        binpath = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(binpath)
