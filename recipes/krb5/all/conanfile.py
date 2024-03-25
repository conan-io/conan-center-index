import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, rm, rmdir, export_conandata_patches, chdir, replace_in_file, apply_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, NMakeToolchain, NMakeDeps, VCVars

required_conan_version = ">=1.54.0"


class Krb5Conan(ConanFile):
    name = "krb5"
    description = ("Kerberos is a network authentication protocol. It is designed to provide strong authentication "
                   "for client/server applications by using secret-key cryptography.")
    # License expression taken from https://packages.fedoraproject.org/pkgs/krb5/krb5-devel/
    license = ("BSD-2-Clause AND (BSD-2-Clause OR GPL-2.0-or-later) AND BSD-3-Clause AND BSD-4-Clause AND FSFULLRWD "
               "AND HPND-export-US AND HPND-export-US-modify AND ISC AND MIT AND MIT-CMU AND OLDAP-2.8 AND RSA-MD")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://web.mit.edu/kerberos/"
    topics = ("kerberos", "network", "authentication", "protocol", "client", "server", "cryptography")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "aesni": [True, False],
        "delayed_initialization": [True, False],
        "kdc_lookaside_cache": [True, False],
        "leash": [True, False],
        "nls": [True, False],
        "pkinit": [True, False],
        "thread": [True, False],
        "use_athena_config": [True, False],
        "use_dns_realms": [True, False],
        "vague_errors": [True, False],
        "with_hesiod": [True, False],
        "with_keyutils": [True, False],
        "with_ldap": [True, False],
        "with_lmdb": [True, False],
        "with_readline": [True, False],
        "with_tcl": [True, False],
        "with_tls": ["openssl", "builtin"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "aesni": True,
        "delayed_initialization": True,
        "kdc_lookaside_cache": True,
        "leash": False,
        "nls": True,
        "pkinit": True,
        "thread": True,
        "use_athena_config": False,
        "use_dns_realms": False,
        "vague_errors": False,
        "with_hesiod": False,
        "with_keyutils": False,
        "with_ldap": False,
        "with_lmdb": True,
        "with_readline": True,
        "with_tcl": False,
        "with_tls": "openssl",
    }
    options_description = {
        "aesni": "Build with AES-NI support",
        "delayed_initialization": "Initialize library code when loaded",
        "kdc_lookaside_cache": "Enable the cache which detects client retransmits",
        "nls": "Enable native language support",
        "pkinit": "PKINIT plugin support",
        "thread": "Enable thread support",
        "use_athena_config": "Build with MIT Project Athena configuration",
        "vague_errors": "Do not send helpful errors to client",
        "with_hesiod": "Compile with hesiod support",
        "with_keyutils": "Link with libkeyutils",
        "with_ldap": "Compile OpenLDAP database backend module",
        "with_lmdb": "Compile LMDB database backend module",
        "with_readline": "Compile with GNU Readline",
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
        if is_msvc(self):
            self.options.rm_safe("thread")
            self.options.rm_safe("with_tls")
            self.options.rm_safe("with_tcl")
            self.options.rm_safe("pkinit")
        else:
            self.options.rm_safe("leash")

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.get_safe("with_tls") == "openssl":
            self.requires("openssl/[>=1.1 <4]")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("libnl/3.9.0")
        if self.options.with_ldap:
            self.requires("openldap/2.6.1")
        if self.options.with_lmdb:
            self.requires("lmdb/0.9.31")
        if self.options.with_readline:
            self.requires("readline/8.2")
        # if self.settings.os != "Windows":
        #     self.requires("e2fsprogs/1.45.6")
        if not is_msvc(self):
            self.requires("libverto/0.3.2")
        if self.options.get_safe("with_tcl"):
            self.requires("tcl/8.6.13")

    def validate(self):
        if self.options.get_safe("pkinit") and self.options.get_safe("with_tls") != "openssl":
            raise ConanInvalidConfiguration("PKINIT plugin support requires OpenSSL")

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.1.0")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("automake/1.16.5")
            self.tool_requires("strawberryperl/5.32.1.1")
        else:
            self.build_requires("automake/1.16.5")
            self.build_requires("bison/3.8.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        if is_msvc(self):
            tc = NMakeToolchain(self)
            env = tc.environment()
            env.define("KRB_INSTALL_DIR", self.package_folder)
            tc.generate(env)

            tc = NMakeDeps(self)
            tc.generate()

            vcvars = VCVars(self)
            vcvars.generate()
        else:
            if not cross_building(self):
                env = VirtualRunEnv(self)
                env.generate(scope="build")
            yes_no = lambda v: "yes" if v else "no"
            tc = AutotoolsToolchain(self)
            # https://web.mit.edu/kerberos/krb5-latest/doc/build/options2configure.html
            tc.configure_args += [
                "--disable-rpath",
                "--with-crypto-impl=openssl",
                "--with-tls-impl=openssl",
                "--without-libedit",
                f"--enable-aesni={yes_no(self.options.aesni)}",
                f"--enable-athena={yes_no(self.options.use_athena_config)}",
                f"--enable-delayed-initialization={yes_no(self.options.delayed_initialization)}",
                f"--enable-dns-for-realm={yes_no(self.options.use_dns_realms)}",
                f"--enable-kdc-lookaside-cache={yes_no(self.options.kdc_lookaside_cache)}",
                f"--enable-nls={yes_no(self.options.nls)}",
                f"--enable-pkinit={yes_no(self.options.pkinit)}",
                f"--enable-shared={yes_no(self.options.shared)}",
                f"--enable-static={yes_no(not self.options.shared)}",
                f"--enable-thread-support={yes_no(self.options.thread)}",
                f"--enable-vague-errors={yes_no(self.options.vague_errors)}",
                f"--with-crypto-impl={self.options.get_safe('with_tls', 'builtin')}",
                f"--with-spake-openssl={yes_no(self.options.get_safe('with_tls') == 'openssl')}",
                f"--with-hesiod={yes_no(self.options.with_hesiod)}",
                f"--with-keyutils={yes_no(self.options.with_keyutils)}",
                f"--with-ldap={yes_no(self.options.with_ldap)}",
                f"--with-lmdb={yes_no(self.options.with_lmdb)}",
                f"--with-netlib={yes_no(self.settings.os in ['Linux', 'FreeBSD'])}",
                f"--with-readline={yes_no(self.options.with_readline)}",
                "--with-system-verto",
                f"--with-tcl={(self.dependencies['tcl'].package_folder if self.options.get_safe('with_tcl') else 'no')}",
            ]
            tc.generate()

            deps = AutotoolsDeps(self)
            deps.generate()
            deps = PkgConfigDeps(self)
            deps.generate()

    def _build_autotools(self):
        autotools = Autotools(self)
        autotools.configure(build_script_folder=os.path.join(self.source_folder, "src"))
        autotools.make()


    @property
    def _nmake_args(self):
        nmake_args = []
        if self.settings.build_type != "Debug":
            nmake_args.append("NODEBUG=1")
        if not self.options.leash:
            nmake_args.append("NO_LEASH=1")
        if self.options.use_dns_realms:
            nmake_args.append("KRB5_USE_DNS_REALMS=1")
        return nmake_args

    def _build_msvc(self):
        with chdir(self, os.path.join(self.source_folder, "src")):
            self.run("nmake -f Makefile.in prep-windows")
            self.run("nmake {}".format(" ".join(self._nmake_args)))

    def build(self):
        if not self.options.shared:
            with chdir(self, os.path.join(self.source_folder,"src", "kadmin", "dbutil")):
                replace_in_file(self, "kdb5_util.c",
                                "krb5_keyblock master_keyblock;",
                                "extern krb5_keyblock master_keyblock;")
            with chdir(self, os.path.join(self.source_folder,"src", "tests", "create")):
                replace_in_file(self, "kdb5_mkdums.c",
                                "krb5_keyblock master_keyblock;",
                                "extern krb5_keyblock master_keyblock;")
                replace_in_file(self, "kdb5_mkdums.c",
                                "krb5_principal master_princ;",
                                "static krb5_principal master_princ;")
                replace_in_file(self, "kdb5_mkdums.c",
                                "krb5_pointer master_random;",
                                "static krb5_pointer master_random;")
            with chdir(self, os.path.join(self.source_folder,"src", "tests", "verify")):
                replace_in_file(self, "kdb5_verify.c",
                                "krb5_keyblock master_keyblock;",
                                "extern krb5_keyblock master_keyblock;")
                replace_in_file(self, "kdb5_verify.c",
                                "krb5_principal master_princ;",
                                "static krb5_principal master_princ;")
        apply_conandata_patches(self)
        if is_msvc(self):
            self._build_msvc()
        else:
            self._build_autotools()

    def package(self):
        copy(self, "NOTICE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            with chdir(self, os.path.join(self.source_folder, "src")):
                self.run("nmake install {}".format(" ".join(self._nmake_args)))
            rm(self, "*.pdb", self.package_folder, recursive=True)
        else:
            autotools = Autotools(self)
            autotools.install()
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "var"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("cmake_target_name", None)

        krb5_lib = "krb5"
        krb5support = "krb5support"
        crypto_libs = []
        gssapi_lib = "gssapi_krb5"
        if is_msvc(self):
            suffix = {
                "x86_64": "64",
                "x86": "32",
            }[str(self.settings.arch)]
            krb5_lib += "_" + suffix
            krb5support = "k5sprt" + suffix
            gssapi_lib = "gssapi" + suffix
        else:
            crypto_libs.append("k5crypto")

        requires = ["openssl::openssl"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            requires.append("libnl::libnl")
        if self.options.with_ldap:
            requires.append("openldap::openldap")
        if self.options.with_lmdb:
            requires.append("lmdb::lmdb")
        if self.options.with_readline:
            requires.append("readline::readline")

        self.cpp_info.components["krb5"].set_property("pkg_config_name", "krb5")
        self.cpp_info.components["krb5"].libdirs.append(os.path.join("lib", "krb5", "plugins", "preauth"))
        self.cpp_info.components["krb5"].libdirs.append(os.path.join("lib", "krb5", "plugins", "tls"))
        self.cpp_info.components["krb5"].libs = ["krb5"]
        self.cpp_info.components["krb5"].requires = ["mit-krb5"]
        self.cpp_info.components["krb5"].libs = ["krb5"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["krb5"].system_libs.extend(["dl", "m", "pthread"])
        self.cpp_info.components["krb5"].requires = requires

        self.cpp_info.components["mit-krb5"].set_property("pkg_config_name", "mit-krb5")
        self.cpp_info.components["mit-krb5"].libs = [krb5_lib] + crypto_libs + [krb5support]
        if not is_msvc(self):
            self.cpp_info.components["mit-krb5"].libs.append("com_err")  # is a common library, that can potentially be packaged (but I don't know who "owns" it)

        if self.options.get_safe("with_tls") == "openssl":
            self.cpp_info.components["mit-krb5"].requires.append("openssl::ssl")
        self.cpp_info.components["mit-krb5"].names["pkg_config"] = "mit-krb5"
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["mit-krb5"].system_libs = ["resolv"]

        self.cpp_info.components["mit-krb5-gssapi"].set_property("pkg_config_name", "mit-krb5-gssapi")
        self.cpp_info.components["mit-krb5-gssapi"].libs = [gssapi_lib]
        self.cpp_info.components["mit-krb5-gssapi"].requires = ["mit-krb5"]
        if not is_msvc(self) and self.settings.os == "Windows" and self.options.get_safe("shared"):
            self.cpp_info.components["mit-krb5-gssapi"].defines.append("GSS_DLL_FILE")

        self.cpp_info.components["krb5-gssapi"].set_property("pkg_config_name", "krb5-gssapi")
        self.cpp_info.components["krb5-gssapi"].requires = ["mit-krb5-gssapi"]

        if not is_msvc(self):
            self.cpp_info.components["gssrpc"].set_property("pkg_config_name", "gssrpc")
            self.cpp_info.components["gssrpc"].libs = ["gssrpc"]
            self.cpp_info.components["gssrpc"].requires = ["mit-krb5-gssapi"]

            self.cpp_info.components["kdb"].set_property("pkg_config_name", "kdb")
            self.cpp_info.components["kdb"].libdirs.append(os.path.join("lib", "krb5", "plugins", "kdb"))
            self.cpp_info.components["kdb"].libs = ["kdb5"]
            self.cpp_info.components["kdb"].requires = ["mit-krb5-gssapi", "mit-krb5", "gssrpc"]

            self.cpp_info.components["kadm-server"].set_property("pkg_config_name", "kadm-server")
            self.cpp_info.components["kadm-server"].libs = ["kadm5srv_mit"]
            self.cpp_info.components["kadm-server"].requires = ["kdb", "mit-krb5-gssapi"]

            self.cpp_info.components["kadm-client"].set_property("pkg_config_name", "kadm-client")
            self.cpp_info.components["kadm-client"].libs = ["kadm5clnt_mit"]
            self.cpp_info.components["kadm-client"].requires = ["mit-krb5-gssapi", "gssrpc"]

            self.cpp_info.components["krad"].libs = ["krad"]
            self.cpp_info.components["krad"].requires = ["krb5", "libverto::libverto"]

            bin_path = os.path.join(self.package_folder, "bin")
            krb5_config = os.path.join(bin_path, "krb5-config").replace("\\", "/")
            self.env_info.KRB5_CONFIG = krb5_config
