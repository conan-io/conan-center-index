from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import VirtualRunEnv
from conan.tools.files import copy, get, rm, rmdir, save
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=2.0"


class LibgcryptConan(ConanFile):
    name = "libgcrypt"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnupg.org/download/index.html#libgcrypt"
    description = "Libgcrypt is a general purpose cryptographic library originally based on code from GnuPG"
    topics = ("gcrypt", "gnupg", "gpg", "crypto", "cryptography")
    license = "LGPL-2.1-or-later"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libcap/[>=2.69 <3]")
        self.requires("libgpg-error/[>=1.61 <2]", transitive_headers=True)

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("This recipe only support Linux. You can contribute Windows and/or Macos support.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        pc_deps = PkgConfigDeps(self)
        pc_deps.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

        tc = AutotoolsToolchain(self)
        libgpg_error = self.dependencies["libgpg-error"]
        tc.configure_args.extend([
            "--disable-doc",
            f"--with-libgpg-error-prefix={libgpg_error.package_folder}",
            f"ac_cv_path_GPGRT_CONFIG={os.path.join(libgpg_error.package_folder, 'bin', 'gpgrt-config')}",
        ])
        tc.generate()

    def _patch_sources(self):
        # Disable the tests subdir
        save(self, os.path.join(self.source_folder, "tests", "Makefile.in"), "all:\ninstall:\n")

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rm(self, "*la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["gcrypt"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
