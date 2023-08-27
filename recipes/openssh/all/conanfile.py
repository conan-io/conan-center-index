from conan import ConanFile
from conan.errors import ConanInvalidConfiguration, ConanException
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

    def _custom_apply_conandata_patches(self):

        if self.conan_data is None:
            raise ConanException("conandata.yml not defined")

        patches = self.conan_data.get('patches')
        if patches is None:
            self.output.info("apply_conandata_patches(): No patches defined in conandata")
            return

        if isinstance(patches, dict):
            assert self.version, "Can only be applied if self.version is already defined"
            entries = patches.get(str(self.version), [])
        elif isinstance(patches, list):
            entries = patches
        else:
            raise ConanException("conandata.yml 'patches' should be a list or a dict {version: list}")
        
        for it in entries:
            if "patch_os" in it:
                patch_os = it.get("patch_os")
                os = self.settings.os

                if patch_os != os:
                    continue

            if "patch_os_version" in it:
                patch_os_version = it.get("patch_os_version")
                os_version = self.settings.get_safe("os.version")

                if patch_os_version != self.settings.get_safe("os.version"):
                    continue

            if "patch_file" in it:
                # The patch files are located in the root src
                entry = it.copy()
                patch_file = entry.pop("patch_file")
                patch_file_path = join(self.export_sources_folder, patch_file)
                if not "patch_description" in entry:
                    entry["patch_description"] = patch_file

                patch(self, patch_file=patch_file_path, **entry)
            elif "patch_string" in it:
                patch(self, **it)
            else:
                raise ConanException("The 'conandata.yml' file needs a 'patch_file' or 'patch_string'"
                                    " entry for every patch to be applied")

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
        self.requires("zlib/[>=1.2.13 <2]")
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
        self._custom_apply_conandata_patches()

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
