import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools import files
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv


required_conan_version = ">=1.54.0"

# Based on https://github.com/madebr/conan-center-index/tree/recipes_wip/recipes/krb5/all
class Krb5Conan(ConanFile):
    name = "krb5"
    description = "Kerberos is a network authentication protocol. It is designed to provide strong authentication " \
                  "for client/server applications by using secret-key cryptography."
    homepage = "https://web.mit.edu/kerberos"
    topics = ("kerberos", "network", "authentication", "protocol", "client", "server", "cryptography")
    license = "LicenseRef-NOTICE"
    url = "https://github.com/conan-io/conan-center-index"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "thread": [True, False],
        "use_dns_realms": [True, False],
        "with_tls": [False, "openssl"],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "thread": True,
        "use_dns_realms": False,
        "with_tls": "openssl",
    }

    settings = "os", "arch", "compiler", "build_type"

    def requirements(self):
        self.requires("libverto/0.3.2")
        if self.options.get_safe("with_tls") == "openssl":
            self.requires("openssl/1.1.1w")
        if self.options.get_safe("with_tcl"):
            self.requires("tcl/8.6.10")


    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} Conan recipe is not prepared for Windows yet. Contributions are welcome!")


    def source(self):
        files.get(self, **self.conan_data["sources"][self.version],
            destination=self.folders.base_source, strip_root=True)


    def layout(self):
        basic_layout(self, src_folder="src")


    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")
        yes_no = lambda v: "yes" if v else "no"
        tc = AutotoolsToolchain(self)

        # fix compiling error
        if self.settings.compiler == 'gcc' and Version(self.settings.compiler.version) >= "10" or self.settings.compiler == 'clang':
            tc.extra_cflags.append('-fcommon')

        tls_impl = {"openssl": "openssl",}.get(str(self.options.get_safe('with_tls')))

        tc.configure_args.extend([
            f"--enable-shared={yes_no(self.options.shared)}",
            f"--enable-static={yes_no(not self.options.shared)}",
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
            "--without-system-verto",
            "--enable-dns-for-realm",
            f"--with-keyutils={self.package_folder}",
            f"--with-tcl={(self.dependencies['tcl'].package_folder if self.options.get_safe('with_tcl') else 'no')}",
        ])
        tc.generate()

        pkg = AutotoolsDeps(self)
        pkg.generate()
        pkg = PkgConfigDeps(self)
        pkg.generate()


    def build(self):
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()


    def build_requirements(self):
        if self.settings.compiler != "msvc":
            self.build_requires("automake/1.16.4")
            self.build_requires("bison/3.7.6")
            self.build_requires("pkgconf/1.7.4")


    def package(self):
        files.copy(self, "NOTICE", src=self.source_folder, dst=os.path.join(self.package_folder,"licenses"))
        autotools = Autotools(self)
        autotools.install()
        fix_apple_shared_install_name(self)
        files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        files.rmdir(self, os.path.join(self.package_folder, "share"))
        files.rmdir(self, os.path.join(self.package_folder, "var"))


    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "krb5")
        self.cpp_info.set_property("cmake_target_name", "krb5::krb5")
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("pkg_config_name", "krb5")

        # krb5::libkrb5
        self.cpp_info.components["mit-krb5"].libs = ["krb5", "k5crypto", "krb5support", "com_err"]
        if self.options.get_safe('with_tls') == "openssl":
            self.cpp_info.components["mit-krb5"].requires = [ "openssl::crypto"]
        self.cpp_info.components["mit-krb5"].names["pkg_config"] = "mit-krb5"
        if self.settings.os == "Linux":
            self.cpp_info.components["mit-krb5"].system_libs = ["resolv"]

        self.cpp_info.components["libkrb5"].libs = []
        self.cpp_info.components["libkrb5"].requires = ["mit-krb5"]
        self.cpp_info.components["libkrb5"].names["pkg_config"] = "krb5"
        self.cpp_info.components["libkrb5"].set_property("cmake_target_name", "krb5::libkrb5")

        # krb5-gssapi:
        self.cpp_info.components["mit-krb5-gssapi"].libs = ["gssapi_krb5"]
        self.cpp_info.components["mit-krb5-gssapi"].requires = ["mit-krb5"]
        self.cpp_info.components["mit-krb5-gssapi"].names["pkg_config"] = "mit-krb5-gssapi"
        self.cpp_info.components["krb5-gssapi"].libs = []
        self.cpp_info.components["krb5-gssapi"].requires = ["mit-krb5-gssapi"]
        self.cpp_info.components["krb5-gssapi"].names["pkg_config"] = "krb5-gssapi"
        self.cpp_info.components["krb5-gssapi"].set_property("cmake_target_name", "krb5::krb5-gssapi")

        # krb5-gssrpc
        self.cpp_info.components["krb5-gssrpc"].libs = ["gssrpc"]
        self.cpp_info.components["krb5-gssrpc"].requires = ["krb5-gssapi"]
        self.cpp_info.components["krb5-gssrpc"].set_property("cmake_target_name", "krb5::krb5-gssrpc")

        # kadm-client
        self.cpp_info.components["kadm-client"].libs = ["kadm5clnt_mit"]
        self.cpp_info.components["kadm-client"].requires = ["krb5-gssapi", "krb5-gssrpc"]
        self.cpp_info.components["kadm-client"].set_property("cmake_target_name", "krb5::kadm-client")

        # kdb5
        self.cpp_info.components["kdb"].libs = ["kdb5"]
        self.cpp_info.components["kdb"].requires = ["libkrb5", "krb5-gssapi", "krb5-gssrpc"]
        self.cpp_info.components["kdb"].set_property("cmake_target_name", "krb5::kdb")

        # kadm-client
        self.cpp_info.components["kadm-server"].libs = ["kadm5srv_mit"]
        self.cpp_info.components["kadm-server"].requires = ["kdb", "krb5-gssapi"]
        self.cpp_info.components["kdb"].set_property("cmake_target_name", "krb5::kadm-server")

        self.cpp_info.components["krad"].libs = ["krad"]
        self.cpp_info.components["krad"].requires = ["libkrb5", "libverto::libverto"]
        self.cpp_info.components["krad"].set_property("cmake_target_name", "krb5::krad")

        krb5_config = os.path.join(self.package_folder, "bin", "krb5-config").replace("\\", "/")
        self.output.info("Appending KRB5_CONFIG environment variable: {}".format(krb5_config))
        self.runenv_info.define_path("KRB5_CONFIG", krb5_config)
