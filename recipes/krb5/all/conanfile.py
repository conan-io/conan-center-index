import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path

required_conan_version = ">=1.54.0"


class Krb5Conan(ConanFile):
    name = "krb5"
    description = "Kerberos 5 network authentication protocol"
    # License expression taken from https://packages.fedoraproject.org/pkgs/krb5/krb5-devel/
    license = ("BSD-2-Clause AND (BSD-2-Clause OR GPL-2.0-or-later) AND BSD-3-Clause AND BSD-4-Clause AND FSFULLRWD "
               "AND HPND-export-US AND HPND-export-US-modify AND ISC AND MIT AND MIT-CMU AND OLDAP-2.8 AND RSA-MD")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://web.mit.edu/kerberos/"
    topics = ("kerberos", "authentication")

    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "aesni": [True, False],
        "delayed_initialization": [True, False],
        "kdc_lookaside_cache": [True, False],
        "nls": [True, False],
        "pkinit": [True, False],
        "thread_support": [True, False],
        "use_athena_config": [True, False],
        "vague_errors": [True, False],
        "with_hesiod": [True, False],
        "with_keyutils": [True, False],
        "with_ldap": [True, False],
        "with_lmdb": [True, False],
        "with_readline": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "aesni": True,
        "delayed_initialization": True,
        "kdc_lookaside_cache": True,
        "nls": True,
        "pkinit": True,
        "thread_support": True,
        "use_athena_config": False,
        "vague_errors": False,
        "with_hesiod": False,
        "with_keyutils": False,
        "with_ldap": False,
        "with_lmdb": True,
        "with_readline": True,
    }
    options_description = {
        "aesni": "Build with AES-NI support",
        "delayed_initialization": "Initialize library code when loaded",
        "kdc_lookaside_cache": "Enable the cache which detects client retransmits",
        "nls": "Enable native language support",
        "pkinit": "PKINIT plugin support",
        "thread_support": "Enable thread support",
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

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openssl/[>=1.1 <4]")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("libnl/3.8.0")
        if self.options.with_ldap:
            self.requires("openldap/2.6.1")
        if self.options.with_lmdb:
            self.requires("lmdb/0.9.29")
        if self.options.with_readline:
            self.requires("readline/8.2")

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("Building with MSVC is not yet supported. Contributions are welcome.")

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.1.0")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        yes_no = lambda v: "yes" if v else "no"
        tc = AutotoolsToolchain(self)
        tc.configure_args += [
            "--disable-rpath",
            "--with-crypto-impl=openssl",
            "--with-tls-impl=openssl",
            "--without-libedit",
            f"--enable-aesni={yes_no(self.options.aesni)}",
            f"--enable-athena={yes_no(self.options.use_athena_config)}",
            f"--enable-delayed-initialization={yes_no(self.options.delayed_initialization)}",
            f"--enable-kdc-lookaside-cache={yes_no(self.options.kdc_lookaside_cache)}",
            f"--enable-nls={yes_no(self.options.nls)}",
            f"--enable-pkinit={yes_no(self.options.pkinit)}",
            f"--enable-shared={yes_no(self.options.shared)}",
            f"--enable-static={yes_no(not self.options.shared)}",
            f"--enable-thread-support={yes_no(self.options.thread_support)}",
            f"--enable-vague-errors={yes_no(self.options.vague_errors)}",
            f"--with-hesiod={yes_no(self.options.with_hesiod)}",
            f"--with-keyutils={yes_no(self.options.with_keyutils)}",
            f"--with-ldap={yes_no(self.options.with_ldap)}",
            f"--with-lmdb={yes_no(self.options.with_lmdb)}",
            f"--with-netlib={yes_no(self.settings.os in ['Linux', 'FreeBSD'])}",
            f"--with-readline={yes_no(self.options.with_readline)}",
        ]
        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

        if is_msvc(self):
            env = Environment()
            automake_conf = self.dependencies.build["automake"].conf_info
            compile_wrapper = unix_path(self, automake_conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, automake_conf.get("user.automake:lib-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f"{ar_wrapper} lib")
            # env.define("NM", "dumpbin -symbols")
            # env.define("OBJDUMP", ":")
            # env.define("RANLIB", ":")
            # env.define("STRIP", ":")
            env.vars(self).save_script("conanbuild_msvc")

    def build(self):
        autotools = Autotools(self)
        autotools.configure(build_script_folder=os.path.join(self.source_folder, "src"))
        autotools.make()

    def package(self):
        copy(self, "NOTICE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "var"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("cmake_target_name", None)

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
        self.cpp_info.components["mit-krb5"].libs = ["krb5", "k5crypto", "com_err", "krb5support"]

        self.cpp_info.components["mit-krb5-gssapi"].set_property("pkg_config_name", "mit-krb5-gssapi")
        self.cpp_info.components["mit-krb5-gssapi"].libs = ["gssapi_krb5"]
        self.cpp_info.components["mit-krb5-gssapi"].requires = ["mit-krb5"]

        self.cpp_info.components["krb5-gssapi"].set_property("pkg_config_name", "krb5-gssapi")
        self.cpp_info.components["krb5-gssapi"].requires = ["mit-krb5-gssapi"]

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
