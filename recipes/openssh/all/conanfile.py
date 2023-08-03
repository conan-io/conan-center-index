from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import patch, copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from os.path import join


required_conan_version = ">=1.54.0"

class PackageConan(ConanFile):
    name = "openssh"
    description = "The OpenSSH (portable) suite of secure connectivity tools"
    license = "BSD"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/openssh/openssh-portable"
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

    def _patch_sources(self):
        print("patching for {}-{}-{}".format(self.version, str(self.settings.os).lower(), self.settings.get_safe("os.version")))

        # general patches
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            print(f"patching general files: {p['patch_file']}")
            patch(self, **p, base_path=self.source_folder)
        
        # os specific patches
        for p in self.conan_data.get("patches", {}).get("{}-{}".format(self.version, str(self.settings.os).lower()), []):
            print(f"patching os specific files: {p['patch_file']}")
            patch(self, **p, base_path=self.source_folder)

        # os version specific patches
        for p in self.conan_data.get("patches", {}).get("{}-{}-{}".format(self.version, str(self.settings.os).lower(), self.settings.get_safe("os.version")), []):
            print(f"patching os version specific: {p['patch_file']}")
            patch(self, **p, base_path=self.source_folder)

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def export_sources(self):
        copy(self, "patches/*.patch", self.recipe_folder, self.export_sources_folder, keep_path=True)

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.12]")
        if self.options.with_openssl:
            self.requires("openssl/1.1.1q")
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
            "--with-openssl={}".format("yes" if self.options.with_openssl else "no"), 
            "--with-pam={}".format("yes" if self.options.with_pam else "no"),
        ])

        if self.options.with_openssl:       
            openssl = self.dependencies["openssl"]     
            tc.configure_args.append("--with-ssl-dir={}".format(openssl.package_folder))

        if self.options.with_sandbox != 'auto':
            tc.configure_args.append("--with-sandbox={}".format(self.options.with_sandbox))

        tc.generate()

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
