import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import patch, copy, get, rmdir, export_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from os.path import join

required_conan_version = ">=1.54.0"


class PackageConan(ConanFile):
    name = "openssh"
    description = "The OpenSSH (portable) suite of secure connectivity tools"
    license = "BSD"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.openssh.com/portable.html"
    topics = ("security", "cryptography", "login", "keychain", "file-sharing")
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_openssl": [True, False],
        "with_pam": [True, False],
        "with_sandbox": ["auto", "no", "capsicum", "darwin", "rlimit", "seccomp_filter", "systrace", "pledge"]
    }
    default_options = {
        "with_openssl": True,
        "with_pam": False,
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
            self.requires("openssl/1.1.1w")
        if self.options.with_pam:
            self.requires("openpam/20190224")

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD", "Neutrino"]:
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on {self.settings.os}.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        ad = AutotoolsDeps(self)
        ad.generate()

        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            "--without-zlib-version-check",
            "--with-openssl={}".format("yes" if self.options.with_openssl else "no"),
            "--with-pam={}".format("yes" if self.options.with_pam else "no"),
        ])

        if self.options.with_openssl:
            openssl = self.dependencies["openssl"]
            tc.configure_args.append("--with-ssl-dir={}".format(openssl.package_folder))

        if self.options.with_sandbox != 'auto':
            tc.configure_args.append("--with-sandbox={}".format(self.options.with_sandbox))

        tc.generate()

    def _patch_sources(self):
        # Usage allowed after consideration with CCI maintainers
        def _allowed_patch(candidate):
            """Allow when no patch_os, or when it matches and no patch_os_version, or when it also matches"""
            return "patch_os" not in candidate or (
                    self.settings.os == candidate["patch_os"] and (
                        "patch_os_version" not in candidate or self.settings.get_safe("os.version") == candidate["patch_os_version"]))

        for it in self.conan_data.get("patches", {}).get(self.version, []):
            if _allowed_patch(it):
                entry = it.copy()
                patch_file = entry.pop("patch_file")
                patch_file_path = os.path.join(self.export_sources_folder, patch_file)
                if "patch_description" not in entry:
                    entry["patch_description"] = patch_file
                patch(self, patch_file=patch_file_path, **entry)

    def build(self):
        self._patch_sources()

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
