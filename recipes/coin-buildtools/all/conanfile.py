import os

from conan import ConanFile
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rename, mkdir
from conan.tools.layout import basic_layout
from conan.tools.microsoft import unix_path

required_conan_version = ">=1.52.0"


class CoinBuildtoolsConan(ConanFile):
    name = "coin-buildtools"
    description = "Macros and patches for GNU autotools for COIN-OR projects."
    topics = ("coin", "autotools")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/coin-or-tools/BuildTools"
    license = "EPL-2.0"

    package_type = "application"
    settings = "os", "arch", "build_type", "compiler"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def requirements(self):
        # https://github.com/coin-or-tools/BuildTools/blob/20208f47f7bbc0056a92adefdfd43fded969f674/install_autotools.sh#L9-L12
        self.requires("autoconf/2.71", run=True)
        self.requires("autoconf-archive/2023.02.20", run=True)
        self.requires("automake/1.16.5", run=True)
        self.requires("libtool/2.4.7", run=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        apply_conandata_patches(self)

    @staticmethod
    def _chmod_plus_x(name):
        if os.name == "posix":
            os.chmod(name, os.stat(name).st_mode | 0o111)

    def package(self):
        resdir = os.path.join(self.package_folder, "res")
        copy(self, "*", self.source_folder, resdir)
        if self.version.startswith("cci."):
            mkdir(self, os.path.join(self.package_folder, "licenses"))
            rename(self, os.path.join(resdir, "LICENSE"),
                   os.path.join(self.package_folder, "licenses", "LICENSE"))
        copy(self, "*.m4", self.source_folder, os.path.join(self.package_folder, "bin"))
        rename(self, os.path.join(resdir, "run_autotools"),
               os.path.join(self.package_folder, "bin", "run_autotools"))
        self._chmod_plus_x(os.path.join(self.package_folder, "bin", "run_autotools"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = ["res"]

        aclocal_dir = unix_path(self, os.path.join(self.package_folder, "res"))
        self.buildenv_info.append_path("ACLOCAL_PATH", aclocal_dir)

        # TODO: Legacy, to be removed on Conan 2.0
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.ACLOCAL_PATH.append(aclocal_dir)
