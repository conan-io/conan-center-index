from conan import ConanFile
from conan.tools.files import get, copy, mkdir, rename, rmdir, export_conandata_patches
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.56.0"


class AutoconfArchiveConan(ConanFile):
    name = "autoconf-archive"
    package_type = "build-scripts"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/autoconf-archive/"
    license = "GPL-2.0-or-later"
    description = "The GNU Autoconf Archive is a collection of more than 500 macros for GNU Autoconf"
    topics = ("conan", "GNU", "autoconf", "autoconf-archive", "macro")
    settings = "os"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install()

        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        mkdir(self, os.path.join(self.package_folder, "res"))
        rename(self, os.path.join(self.package_folder, "share", "aclocal"),
                     os.path.join(self.package_folder, "res", "aclocal"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = ["res/aclocal"]

        # Use ACLOCAL_PATH to access the .m4 files provided with autoconf-archive
        aclocal_path = os.path.join(self.package_folder, "res", "aclocal")
        self.buildenv_info.append_path("ACLOCAL_PATH", aclocal_path)

        # Remove for Conan 2.0
        aclocal_path = "/" + aclocal_path.replace("\\", "/").replace(":", "") # Can't use unix_path with Conan 2.0
        self.output.info(f'Appending ACLOCAL_PATH env: {aclocal_path}')
        self.env_info.ACLOCAL_PATH.append(aclocal_path)
        self.output.info("Appending AUTOMAKE_CONAN_INCLUDES environment var: {}".format(aclocal_path))
        self.env_info.AUTOMAKE_CONAN_INCLUDES.append(aclocal_path)
