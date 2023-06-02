from conan import ConanFile
from conans import tools
from conan.tools.env import VirtualBuildEnv
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, rmdir, chdir, replace_in_file, export_conandata_patches, apply_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsToolchain,AutotoolsDeps, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from contextlib import contextmanager
import glob
import os

required_conan_version = ">=1.52.0"


class Krb5Conan(ConanFile):
    name = "krb5"
    description = "Kerberos is a network authentication protocol. It is designed to provide strong authentication " \
                  "for client/server applications by using secret-key cryptography."
    homepage = "https://web.mit.edu/kerberos"
    topics = ("kerberos", "network", "authentication", "protocol", "client", "server", "cryptography")
    license = "NOTICE"
    url = "https://github.com/conan-io/conan-center-index"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "thread": [True, False],
        "use_dns_realms": [True, False],
        "leash": [True, False],
        "with_tls": [False, "openssl"],
        "with_tcl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "thread": True,
        "use_dns_realms": False,
        "leash": False,
        "with_tls": "openssl",
        "with_tcl": False,
    }
    settings = "os", "arch", "compiler", "build_type"

    exports_sources = "patches/*"

    def layout(self):
        basic_layout(self, src_folder="src")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def validate(self):
        if is_msvc(self) and not self.options.shared:
            raise ConanInvalidConfiguration("Visual Studio only builds shared libraries")

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
        if is_msvc(self):
            self.options.rm_safe("thread")
            self.options.rm_safe("with_tls")
            self.options.rm_safe("with_tcl")
        else:
            self.options.rm_safe("leash")

    def configure(self):
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tls_impl = {
            "openssl": "openssl",
        }.get(str(self.options.get_safe('with_tls')))
        tc.configure_args.extend([
            f"--enable-thread-support={yes_no(self.options.get_safe('thread'))}",
            f"--enable-dns-for-realm={yes_no(self.options.use_dns_realms)}",
            f"--enable-pkinit={yes_no(self.options.get_safe('with_tls'))}",
            f"--with-crypto-impl={(tls_impl or 'builtin')}",
            f"--with-spake-openssl={yes_no(self.options.get_safe('with_tls') == 'openssl')}",
            "--disable-nls",
            "--disable-rpath",
            "--without-libedit",
            "--without-readline",
            "--with-system-verto",
            # "--with-system-et}",
            # "--with-system-ss}",
            f"--with-tcl={(self.deps_cpp_info['tcl'].rootpath if self.options.get_safe('with_tcl') else 'no')}",
            ])
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()
        pkg = PkgConfigDeps(self)
        pkg.generate()

    def requirements(self):
        # if self.settings.os != "Windows":
        #     self.requires("e2fsprogs/1.45.6")
        if not is_msvc(self):
            self.requires("libverto/0.3.2")
        if self.options.get_safe("with_tls") == "openssl":
            self.requires("openssl/[>=1.1 <4]")
        if self.options.get_safe("with_tcl"):
            self.requires("tcl/8.6.11")

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/1.9.3")
        if not is_msvc(self):
            self.build_requires("automake/1.16.5")
            self.build_requires("bison/3.8.2")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def _build_autotools(self):
        tools.save("skiptests", "")

        # with chdir(self, os.path.join(self.source_folder,"src")):
        #     replace_in_file(self,"aclocal.m4", "AC_CONFIG_AUX_DIR(", "echo \"Hello world\"\n\nAC_CONFIG_AUX_DIR(")
        #     self.run("{} -fiv".format(tools.get_env("AUTORECONF")), run_environment=True, win_bash=tools.os_info.is_windows)
        autotools = Autotools(self)
        autotools.configure(os.path.join(self.source_folder,"src"))
        autotools.make()

    @contextmanager
    def _msvc_context(self):
        env = {
            "KRB_INSTALL_DIR": self.package_folder,
        }
        with tools.environment_append(env):
            with tools.vcvars(self.settings):
                yield

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
            with self._msvc_context():
                self.run("nmake -f Makefile.in prep-windows", run_environment=True, win_bash=tools.os_info.is_windows)
                self.run("nmake {}".format(" ".join(self._nmake_args)), run_environment=True, win_bash=tools.os_info.is_windows)

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
        copy(self, "NOTICE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            with chdir(self, os.path.join(self.source_folder, "src")):
                with self._msvc_context():
                    self.run("nmake install {}".format(" ".join(self._nmake_args)), run_environment=True, win_bash=tools.os_info.is_windows)

            for pdb in glob.glob(os.path.join(self.package_folder, "bin", "*.pdb")):
                os.unlink(pdb)
        else:
            autotools = Autotools(self)
            autotools.install()

            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "share"))
            rmdir(self, os.path.join(self.package_folder, "var"))

    def package_info(self):
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

        self.cpp_info.components["mit-krb5"].libs = [krb5_lib] + crypto_libs + [krb5support]
        if not is_msvc(self):
            self.cpp_info.components["mit-krb5"].libs.append("com_err")  # is a common library, that can potentially be packaged (but I don't know who "owns" it)

        if self.options.get_safe('with_tls') == "openssl":
            self.cpp_info.components["mit-krb5"].requires.append("openssl::ssl")
        self.cpp_info.components["mit-krb5"].names["pkg_config"] = "mit-krb5"
        if self.settings.os == "Linux":
            self.cpp_info.components["mit-krb5"].system_libs = ["resolv"]

        self.cpp_info.components["libkrb5"].libs = []
        self.cpp_info.components["libkrb5"].requires = ["mit-krb5"]
        self.cpp_info.components["libkrb5"].names["pkg_config"] = "krb5"

        self.cpp_info.components["mit-krb5-gssapi"].libs = [gssapi_lib]
        self.cpp_info.components["mit-krb5-gssapi"].requires = ["mit-krb5"]
        self.cpp_info.components["mit-krb5-gssapi"].names["pkg_config"] = "mit-krb5-gssapi"
        if not is_msvc(self) and self.settings.os == "Windows" and self.options.get_safe("shared"):
            self.cpp_info.components["mit-krb5-gssapi"].defines.append("GSS_DLL_FILE")

        self.cpp_info.components["krb5-gssapi"].libs = []
        self.cpp_info.components["krb5-gssapi"].requires = ["mit-krb5-gssapi"]
        self.cpp_info.components["krb5-gssapi"].names["pkg_config"] = "krb5-gssapi"

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        if not is_msvc(self):
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

            krb5_config = os.path.join(bin_path, "krb5-config").replace("\\", "/")
            self.output.info("Appending KRB5_CONFIG environment variable: {}".format(krb5_config))
            self.env_info.KRB5_CONFIG = krb5_config
