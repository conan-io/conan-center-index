from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.files import copy, get, rmdir
from conan.tools.layout import basic_layout
from conan.tools.apple import is_apple_os
import os

required_conan_version = ">=1.60.0"

class RsyncConan(ConanFile):
    name = "rsync"
    description = "rsync is an open source utility that provides fast incremental file transfer"
    topics = ("backup", "transferring", "file-transfer", "ssh", "compression")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://rsync.samba.org/"
    license = ("GPL-3.0", "LGPL-3.0")
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "with_zlib": [True, False],
        "with_openssl": [True, False],
        "with_zstd": [True, False],
        "with_xxhash": [True, False],
        "with_lz4": [True, False],
        "enable_acl": [True, False]
    }
    default_options = {
        "with_zlib": True,
        "with_openssl": True,
        "with_zstd": True,
        "with_xxhash": True,
        "with_lz4": True,
        "enable_acl": False
    }
    
    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package_id(self):
        del self.info.settings.compiler
    
    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")

        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")

        if self.options.with_zstd:
            self.requires("zstd/1.5.5")

        if self.options.with_lz4:
            self.requires("lz4/1.9.2")

        if self.options.with_xxhash:
            self.requires("xxhash/0.8.1")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on Windows.")        

        if is_apple_os(self):
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on Apple systems.")        

    def generate(self):
        ad = AutotoolsDeps(self)
        ad.generate()

        yes_no = lambda v: "yes" if v else "no"
        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            f"--enable-acl-support={yes_no(self.options.enable_acl)}",
            f"--with-included-zlib={yes_no(not self.options.with_zlib)}",            
            "--disable-openssl" if not self.options.with_openssl else "--enable-openssl",
            f"--with-zstd={yes_no(self.options.with_zstd)}",
            f"--with-lz4={yes_no(self.options.with_lz4)}",
            f"--with-xxhash={yes_no(self.options.with_xxhash)}",

            "--enable-manpages=no",
        ])        

        if self.settings.os == "Neutrino":
            tc.extra_defines.append("MAKEDEV_TAKES_3_ARGS")

        tc.generate()

    def build(self):
        autotools = Autotools(self)  
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)  
        autotools.install()

        rmdir(self, os.path.join(self.package_folder, "share"))
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"), ignore_case=True)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        # TODO: Remove after dropping Conan 1.x from ConanCenterIndex
        bindir = os.path.join(self.package_folder, "bin")
        self.runenv_info.prepend_path("PATH", bindir)
