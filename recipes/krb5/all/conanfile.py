from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, rmdir, export_conandata_patches, apply_conandata_patches, chdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.54.0"

class Krb5Conan(ConanFile):
    name = "krb5"
    description = "Kerberos is a network authentication protocol. It is designed to provide strong authentication " \
                  "for client/server applications by using secret-key cryptography."
    homepage = "https://web.mit.edu/kerberos"
    topics = ("kerberos", "network", "authentication", "protocol", "client", "server", "cryptography")
    license = "LicenseRef-NOTICE"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "shared-library"
    options = {
        "use_thread": [True, False],
        "use_dns_realms": [True, False],
        "with_tls": [False, "openssl"],
    }
    default_options = {
        "use_thread": True,
        "use_dns_realms": False,
        "with_tls": "openssl"
    }
    options_description = {
        "use_thread": "Enable thread support",
        "use_dns_realms": "Enable DNS for realms",
        "with_tls": "Enable TLS support with OpenSSL",
    }
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.ref} Conan recipe is not prepared for Windows yet. Contributions are welcome!")
        if self.settings.os == "Macos":
            raise ConanInvalidConfiguration(f"{self.ref} Conan recipe is not prepared for Macos yet. Contributions are welcome!")
        if self.options.with_tls == "openssl" and not self.dependencies["openssl"].options.shared:
            # k5tls does not respect linkage order, it passes krb5 and krb5support before openssl to the linker, which causes linking errors
            # gcc -shared -fPIC -Wl,-h,k5tls.so.0 -Wl,--no-undefined -o k5tls.so openssl.so notls.so -L../../../lib -lkrb5 -lkrb5support ...
            # /usr/bin/ld: /.../lib/libssl.a(libssl-lib-ssl_cert_comp.o): in function `OSSL_COMP_CERT_from_uncompressed_data':
            #     ssl_cert_comp.c:(.text+0x3d1): undefined reference to `COMP_CTX_free'
            raise ConanInvalidConfiguration(f"{self.ref} building with static OpenSSL generates linking errors. Please use '-o openssl/*:shared=True'")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tls_impl = {"openssl": "openssl",}.get(str(self.options.get_safe('with_tls')))
        tc.configure_args.extend([
            f"--enable-thread-support={yes_no(self.options.get_safe('use_thread'))}",
            f"--enable-dns-for-realm={yes_no(self.options.use_dns_realms)}",
            f"--enable-pkinit={yes_no(self.options.get_safe('with_tls'))}",
            f"--with-crypto-impl={(tls_impl or 'builtin')}",
            f"--with-spake-openssl={yes_no(self.options.get_safe('with_tls') == 'openssl')}",
            f"--with-tls-impl={(tls_impl or 'no')}",
            "--disable-nls",
            "--disable-rpath",
            "--without-libedit",
            "--without-readline",
            "--with-system-verto",
            "--enable-dns-for-realm",
            f"--with-keyutils={self.package_folder}",
            f"--with-tcl={(self.dependencies['tcl'].package_folder if self.options.get_safe('with_tcl') else 'no')}",
            ])
        tc.generate()

        pkg = AutotoolsDeps(self)
        pkg.generate()
        pkg = PkgConfigDeps(self)
        pkg.generate()

    def requirements(self):
        self.requires("libverto/0.3.2")
        if self.options.get_safe("with_tls") == "openssl":
            self.requires("openssl/[>=1.1 <4]")
        if self.options.get_safe("with_tcl"):
            self.requires("tcl/8.6.11")

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/1.9.3")
        self.build_requires("automake/1.16.5")
        self.build_requires("bison/3.8.2")

    def build(self):
        apply_conandata_patches(self)
        with chdir(self, os.path.join(self.source_folder, "src")):
            self.run("autoreconf -vif")
        autotools = Autotools(self)
        autotools.configure(build_script_folder=os.path.join(self.source_folder, "src"))
        autotools.make()

    def package(self):
        copy(self, "NOTICE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "var"))

    def package_info(self):
        self.cpp_info.components["mit-krb5"].libs = ["krb5", "k5crypto", "com_err"]
        if self.options.get_safe('with_tls') == "openssl":
            self.cpp_info.components["mit-krb5"].requires = ["openssl::crypto"]
        self.cpp_info.components["mit-krb5"].names["pkg_config"] = "mit-krb5"
        if self.settings.os == "Linux":
            self.cpp_info.components["mit-krb5"].system_libs = ["resolv"]

        self.cpp_info.components["libkrb5"].libs = []
        self.cpp_info.components["libkrb5"].requires = ["mit-krb5"]
        self.cpp_info.components["libkrb5"].names["pkg_config"] = "krb5"

        self.cpp_info.components["mit-krb5-gssapi"].libs = ["gssapi_krb5"]
        self.cpp_info.components["mit-krb5-gssapi"].requires = ["mit-krb5"]
        self.cpp_info.components["mit-krb5-gssapi"].names["pkg_config"] = "mit-krb5-gssapi"

        self.cpp_info.components["krb5-gssapi"].libs = []
        self.cpp_info.components["krb5-gssapi"].requires = ["mit-krb5-gssapi"]
        self.cpp_info.components["krb5-gssapi"].names["pkg_config"] = "krb5-gssapi"

        self.cpp_info.components["gssrpc"].libs = ["gssrpc"]
        self.cpp_info.components["gssrpc"].requires = ["mit-krb5-gssapi"]
        self.cpp_info.components["gssrpc"].names["pkg_config"] = "gssrpc"

        self.cpp_info.components["kadm-client"].libs = ["kadm5clnt_mit"]
        self.cpp_info.components["kadm-client"].requires = ["mit-krb5-gssapi", "gssrpc"]
        self.cpp_info.components["kadm-client"].names["pkg_config"] = "kadm-client"

        self.cpp_info.components["kdb"].libs = ["kdb5"]
        self.cpp_info.components["kdb"].requires = ["mit-krb5-gssapi", "mit-krb5", "gssrpc"]
        self.cpp_info.components["kdb"].names["pkg_config"] = "kdb-client"

        self.cpp_info.components["kadm-server"].libs = ["kadm5srv_mit"]
        self.cpp_info.components["kadm-server"].requires = ["kdb", "mit-krb5-gssapi"]
        self.cpp_info.components["kadm-server"].names["pkg_config"] = "kadm-server"

        self.cpp_info.components["krad"].libs = ["krad"]
        self.cpp_info.components["krad"].requires = ["libkrb5", "libverto::libverto"]

        krb5_config = os.path.join(self.package_folder, "bin", "krb5-config").replace("\\", "/")
        self.output.info("Appending KRB5_CONFIG environment variable: {}".format(krb5_config))
        self.runenv_info.define_path("KRB5_CONFIG", krb5_config)
