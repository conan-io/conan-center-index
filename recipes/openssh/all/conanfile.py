from os.path import join

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, replace_in_file, rmdir, export_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout

required_conan_version = ">=1.54.0"


class PackageConan(ConanFile):
    name = "openssh"
    description = "The OpenSSH (portable) suite of secure connectivity tools"
    license = "SSH-OpenSSH"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.openssh.com/portable.html"
    topics = ("security", "cryptography", "login", "keychain", "file-sharing", "ssh")
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_libcrypto": [False, "libressl", "openssl"],
        "with_pam": [False, "openpam"],  # linux-pam and Solaris PAM are also supported
        "with_selinux": [True, False],
        "with_libedit": [True, False],
        "with_strip": [True, False],
        "with_sandbox": [False, "auto", "capsicum", "darwin", "rlimit", "seccomp_filter", "systrace", "pledge"]
    }
    default_options = {
        "with_libcrypto": "openssl",
        "with_pam": False,
        "with_selinux": False,
        "with_libedit": False,
        "with_strip": True,
        "with_sandbox": "auto"
    }

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_libcrypto == "openssl":
            self.requires("openssl/[>=1.1 <4]")
        elif self.options.with_libcrypto == "libressl":
            self.requires("libressl/3.9.1")
        if self.options.with_pam == "openpam":
            self.requires("openpam/20190224")
        if self.options.with_libedit:
            self.requires("editline/3.1")

    def validate(self):
        if self.settings.os in ["baremetal", "Windows"]:
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on {self.settings.os}.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        if self.version in ["9.1p1", "9.6p1"]:
            # Backport configure script fix to accept OpenSSL versions in the 3.x series
            # See https://github.com/openssh/openssh-portable/commit/2eded551ba96e66bc3afbbcc883812c2eac02bd7
            replace_in_file(self, join(self.source_folder, "configure"), "300*", "30*")

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        ad = AutotoolsDeps(self)
        ad.generate()

        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--without-zlib-version-check")

        if not self.options.with_strip:
            tc.configure_args.append("--disable-strip")

        if self.options.with_selinux:
            tc.configure_args.append("--with-selinux")

        if self.options.with_pam:
            tc.configure_args.append("--with-pam")

        if self.options.with_libedit:
            editline = self.dependencies["editline"]
            tc.configure_args.append("--with-libedit={}".format(editline.package_folder))

        if self.options.with_libcrypto == "openssl":
            openssl = self.dependencies["openssl"]
            tc.configure_args.append("--with-ssl-dir={}".format(openssl.package_folder))
            # It needs libcrypto.so in build time context
            if openssl.options.shared:
                env = VirtualRunEnv(self)
                env.generate(scope="build")
        elif self.options.with_libcrypto == "libressl":
            libressl = self.dependencies["libressl"]
            tc.configure_args.append("--with-ssl-dir={}".format(libressl.package_folder))
        else:
            tc.configure_args.append("--without-openssl")

        if self.options.with_sandbox != 'auto':
            tc.configure_args.append("--with-sandbox={}".format(self.options.with_sandbox or "no"))

        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)

        install_target = 'install-nokeys' if cross_building(self) else 'install'
        autotools.install(target=install_target)

        copy(self, "LICENCE", src=self.source_folder, dst=join(self.package_folder, "licenses"), ignore_case=True)
        copy(self, "*", src=join(self.package_folder, "libexec"), dst=join(self.package_folder, "bin"), ignore_case=True)

        rmdir(self, join(self.package_folder, "etc"))
        rmdir(self, join(self.package_folder, "var"))
        rmdir(self, join(self.package_folder, "share"))
        rmdir(self, join(self.package_folder, "libexec"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        bindir = join(self.package_folder, "bin")
        self.runenv_info.prepend_path("PATH", bindir)
