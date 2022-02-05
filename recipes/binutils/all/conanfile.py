import os
import re
from glob import glob

from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conans import tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.43.0"


class BinutilsConan(ConanFile):
    name = "binutils"
    description = "a collection of binary tools"
    topics = ("gnu", "compilation", "tools")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/binutils"
    license = "GPL-2.0-or-later"

    settings = "os", "arch", "compiler", "build_type"

    _source_subfolder = "source_subfolder"

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("This recipes supports only Linux and FreeBSD")

    def package_id(self):
        del self.info.settings.compiler

    def requirements(self):
        self.requires("zlib/1.2.11")
        self.requires("readline/8.0")

    def generate(self):
        ad = AutotoolsDeps(self)
        # this can be removed if conan >= 1.44.0 due to https://github.com/conan-io/conan/pull/10192
        for m in re.finditer("-Wl,-rpath,\"[^\"]+\"", ad.vars()["LDFLAGS"]):
            ad.environment.remove("LDFLAGS", m[0])
        ad.generate()

        ac = AutotoolsToolchain(self)
        ac.default_configure_install_args = True
        ac.configure_args.extend(["--with-system-zlib", "--with-system-readline"])
        ac.generate()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def build(self):
        at = Autotools(self)
        at.configure(build_script_folder=self._source_subfolder)
        at.make()

    def package(self):
        self.copy(pattern="COPYING*", dst="licenses", src=self._source_subfolder)

        at = Autotools(self)
        at.install()

        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        tools.rmdir(os.path.join(self.package_folder, "share"))
        for dir in glob(os.path.join(self.package_folder, "{}*".format(self.settings.arch))):
            tools.rmdir(dir)

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
