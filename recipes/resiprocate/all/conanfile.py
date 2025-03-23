import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import cross_building
from conan.tools.env import VirtualRunEnv
from conan.tools.files import copy, get, rm, rmdir, chdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout

required_conan_version = ">=1.53.0"


class ResiprocateConan(ConanFile):
    name = "resiprocate"
    description = (
        "The project is dedicated to maintaining a complete, correct, "
        "and commercially usable implementation of SIP and a few related protocols."
    )
    license = "VSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/resiprocate/resiprocate/wiki/"
    topics = ("sip", "voip", "communication", "signaling")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ssl": [True, False],
        "with_postgresql": [True, False],
        "with_mysql": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ssl": True,
        "with_postgresql": True,
        "with_mysql": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.os == "Windows" or is_apple_os(self):
            # FIXME: unreleased versions of resiprocate use CMake and should support Windows and macOS
            raise ConanInvalidConfiguration(f"reSIProcate recipe does not currently support {self.settings.os}.")
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_ssl:
            self.requires("openssl/1.1.1w")  # OpenSSL 3.x is not supported
        if self.options.with_postgresql:
            self.requires("libpq/15.4")
        if self.options.with_mysql:
            self.requires("libmysqlclient/8.1.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if not cross_building(self):
            venv = VirtualRunEnv(self)
            venv.generate(scope="build")
        tc = AutotoolsToolchain(self)
        # These options do not support yes/no
        if self.options.with_ssl:
            tc.configure_args.append("--with-ssl")
        if self.options.with_mysql:
            tc.configure_args.append("--with-mysql")
        if self.options.with_postgresql:
            tc.configure_args.append("--with-postgresql")
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install()
        rmdir(self, os.path.join(os.path.join(self.package_folder, "share")))
        rm(self, "*.la", os.path.join(self.package_folder), recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["resip", "rutil", "dum", "resipares"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs = ["pthread"]

        # TODO: Legacy, to be removed on Conan 2.0
        bin_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_path)
