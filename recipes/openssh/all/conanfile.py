from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, rmdir, export_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from os.path import join

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
        "with_openssl": [True, False],
        "with_pam": [None, "openpam"],
        "with_selinux": [True, False],
        "with_libedit": [True, False],
        "with_sandbox": ["auto", "no", "capsicum", "darwin", "rlimit", "seccomp_filter", "systrace", "pledge"]
    }
    default_options = {
        "with_openssl": True,
        "with_pam": None,
        "with_selinux": False,
        "with_libedit": False,
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
        if self.options.with_openssl:
            if self.version == "8.1p1":
                self.requires("openssl/[>=1.1 <=3.0]")
            else:
                self.requires("openssl/[>=1.1 <=3.1]")
        if self.options.with_pam == "openpam":
            self.requires("openpam/20190224")
        if self.options.with_libedit:
            self.requires("editline/3.1")

    def validate(self):
        if self.settings.os in ["baremetal", "Windows"]:
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on {self.settings.os}.")

        if self.settings.os in ["Macos"] and self.version == "8.1p1":
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on {self.settings.os}.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        ad = AutotoolsDeps(self)
        ad.generate()

        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--without-zlib-version-check")

        if self.options.with_selinux:
            tc.configure_args.append("--with-selinux")

        if self.options.with_pam:
            tc.configure_args.append("--with-pam")

        if self.options.with_libedit:
            editline = self.dependencies["editline"]
            tc.configure_args.append("--with-libedit={}".format(editline.package_folder))

        if self.options.with_openssl:
            openssl = self.dependencies["openssl"]
            tc.configure_args.append("--with-ssl-dir={}".format(openssl.package_folder))
        else:
            tc.configure_args.append("--without-openssl")

        if self.options.with_sandbox != 'auto':
            tc.configure_args.append("--with-sandbox={}".format(self.options.with_sandbox))

        tc.generate()

    def build(self):
        autotools = Autotools(self)
        env = VirtualRunEnv(self)
        with env.vars().apply():
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
