from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import XCRun
from conan.tools.build import cross_building
from conan.tools.env import VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.54.0"


class LdnsConan(ConanFile):
    name = "ldns"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.nlnetlabs.nl/projects/ldns"
    description = "LDNS is a DNS library that facilitates DNS tool programming"
    topics = ("dns")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openssl/1.1.1t")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Windows is not supported by the ldns recipe. Contributions are welcome.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        # This fixes the issue of linking against ldns in combination of openssl:shared=False, ldns:shared=True, and an older GCC:
        # > hidden symbol `pthread_atfork' in /usr/lib/x86_64-linux-gnu/libpthread_nonshared.a(pthread_atfork.oS) is referenced by DSO
        # OpenSSL adds -lpthread to link POSIX thread library explicitly. That is not correct because using the library
        # may require setting various defines on compilation as well. The compiler has a dedicated -pthread option for that.
        tc = AutotoolsDeps(self)
        tc.environment.remove("LIBS", "-lpthread")
        tc.environment.append("CFLAGS", "-pthread")
        tc.generate()

        tc = AutotoolsToolchain(self)
        def yes_no(v): return "yes" if v else "no"
        tc.configure_args.extend([
            "--disable-rpath",
            f"--with-ssl={self.dependencies['openssl'].package_folder}",
            # DNSSEC algorithm support
            "--enable-ecdsa",
            "--enable-ed25519",
            "--enable-ed448",
            "--disable-dsa",
            "--disable-gost",
            "--enable-full-dane",
            # tooling
            "--disable-ldns-config",
            "--without-drill",
            "--without-examples",
            # library bindings
            "--without-pyldns",
            "--without-p5-dns-ldns",
        ])
        if self.settings.compiler == "apple-clang":
            tc.configure_args.append(f"--with-xcode-sdk={XCRun(self).sdk_version}")
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        print(self.package_folder)
        autotools = Autotools(self)
        for target in ["install-h", "install-lib"]:
            autotools.install(target=target)
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.libs = ["ldns"]
