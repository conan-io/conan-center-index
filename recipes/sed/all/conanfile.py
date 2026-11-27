import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc

required_conan_version = ">=2.4"


class SedConan(ConanFile):
    name = "sed"
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/sed/"
    description = "GNU sed, the GNU stream editor"
    topics = ("stream-editor", "text-processing")
    package_type = "application"
    languages = "C"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration(
                f"{self.ref} does not support MSVC, use a MinGW (gcc) toolchain on Windows"
            )

    def build_requirements(self):
        if self.settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.extend(
            [
                "--disable-dependency-tracking",
                "--disable-acl",
                "--without-selinux",
                "--disable-nls",
            ]
        )
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(
            self,
            "COPYING*",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        # Autoconf-generated scripts honour the SED variable
        sed_bin = os.path.join(self.package_folder, "bin", "sed")
        self.runenv_info.define_path("SED", sed_bin)
        self.buildenv_info.define_path("SED", sed_bin)
