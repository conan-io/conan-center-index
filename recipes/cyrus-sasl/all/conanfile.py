from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import unix_path
import os
import shutil

required_conan_version = ">=1.51.1"


class CyrusSaslConan(ConanFile):
    name = "cyrus-sasl"
    license = "BSD-4-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.cyrusimap.org/sasl/"
    description = (
        "This is the Cyrus SASL API implementation. "
        "It can be used on the client or server side "
        "to provide authentication and authorization services."
    )
    topics = ("sasl", "authentication", "authorization")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False],
        "with_cram": [True, False],
        "with_digest": [True, False],
        "with_scram": [True, False],
        "with_otp": [True, False],
        "with_krb4": [True, False],
        "with_gssapi": [True, False],
        "with_plain": [True, False],
        "with_anon": [True, False],
        "with_postgresql": [True, False],
        "with_mysql": [True, False],
        "with_sqlite3": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": True,
        "with_cram": True,
        "with_digest": True,
        "with_scram": True,
        "with_otp": True,
        "with_krb4": True,
        "with_gssapi": False, # FIXME: should be True
        "with_plain": True,
        "with_anon": True,
        "with_postgresql": False,
        "with_mysql": False,
        "with_sqlite3": False,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/1.1.1q")
        if self.options.with_postgresql:
            self.requires("libpq/14.5")
        if self.options.with_mysql:
            self.requires("libmysqlclient/8.0.30")
        if self.options.with_sqlite3:
            self.requires("sqlite3/3.39.4")
        if self.options.with_gssapi:
            raise ConanInvalidConfiguration("with_gssapi requires krb5 recipe, not yet available in CCI")
            self.requires("krb5/1.18.3")

    def validate(self):
        if self.info.settings.os == "Windows":
            raise ConanInvalidConfiguration(
                "Cyrus SASL package is not compatible with Windows yet."
            )

    def build_requirements(self):
        self.tool_requires("gnu-config/cci.20210814")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", default=False, check_type=bool):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        rootpath_no = lambda v, req: unix_path(self, self.dependencies[req].package_folder) if v else "no"
        tc.configure_args.extend([
            "--disable-sample",
            "--disable-macos-framework",
            "--with-dblib=none",
            "--with-openssl={}".format(yes_no(self.options.with_openssl)),
            "--enable-digest={}".format(yes_no(self.options.with_digest)),
            "--enable-scram={}".format(yes_no(self.options.with_scram)),
            "--enable-otp={}".format(yes_no(self.options.with_otp)),
            "--enable-krb4={}".format(yes_no(self.options.with_krb4)),
            "--enable-gssapi={}".format(yes_no(self.options.with_gssapi)),
            "--enable-plain={}".format(yes_no(self.options.with_plain)),
            "--enable-anon={}".format(yes_no(self.options.with_anon)),
            "--enable-sql={}".format(
                yes_no(self.options.with_postgresql or self.options.with_mysql or self.options.with_sqlite3),
            ),
            "--with-pgsql={}".format(rootpath_no(self.options.with_postgresql, "libpq")),
            "--with-mysql={}".format(rootpath_no(self.options.with_mysql, "libmysqlclient")),
            "--without-sqlite",
            "--with-sqlite3={}".format(rootpath_no(self.options.with_sqlite3, "sqlite3")),
        ])
        if self.options.with_gssapi:
            tc.configure_args.append("--with-gss_impl=mit")
        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

    def _patch_sources(self):
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB,
                    os.path.join(self.source_folder, "config", "config.sub"))
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS,
                    os.path.join(self.source_folder, "config", "config.guess"))
        # relocatable executable & shared libs on macOS
        replace_in_file(self, os.path.join(self.source_folder, "configure"), "-install_name \\$rpath/", "-install_name @rpath/")

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        # TODO: replace by autotools.install() once https://github.com/conan-io/conan/issues/12153 fixed
        autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"), recursive=True)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libsasl2")
        self.cpp_info.libs = ["sasl2"]

        # TODO: to remove in conan v2
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bindir}")
        self.env_info.PATH.append(bindir)
