import glob
import os
import shutil

from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


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

    topics = ("SASL", "authentication", "authorization")
    settings = "os", "compiler", "build_type", "arch"
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
    exports_sources = ("patches/**",)
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(
                "Cyrus SASL package is not compatible with Windows yet."
            )

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/1.1.1k")
        if self.options.with_postgresql:
            self.requires("libpq/13.3")
        if self.options.with_mysql:
            self.requires("libmysqlclient/8.0.25")
        if self.options.with_sqlite3:
            self.requires("sqlite3/3.36.0")
        if self.options.with_gssapi:
            raise ConanInvalidConfiguration("with_gssapi requires krb5 recipe, not yet available in CCI")
            self.requires("krb5/1.18.3")

    def build_requirements(self):
        self.build_requires("gnu-config/cci.20201022")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", None) or self.deps_user_info

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB,
                    os.path.join(self._source_subfolder, "config", "config.sub"))
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS,
                    os.path.join(self._source_subfolder, "config", "config.guess"))

    def _configure_autotools(self):
        if self._autotools is None:
            self._autotools = AutoToolsBuildEnvironment(
                self, win_bash=tools.os_info.is_windows
            )
            configure_args = [
                "--disable-sample",
                "--disable-macos-framework",
                "--with-dblib=none",
            ]
            if self.options.shared:
                configure_args.extend(["--enable-shared", "--disable-static"])
            else:
                configure_args.extend(["--disable-shared", "--enable-static"])

            if not self.options.with_openssl:
                configure_args.append("--without-openssl")

            if not self.options.with_digest:
                configure_args.append("--disable-digest")

            if not self.options.with_scram:
                configure_args.append("--disable-scram")

            if not self.options.with_otp:
                configure_args.append("--disable-otp")

            if not self.options.with_krb4:
                configure_args.append("--disable-krb4")

            if self.options.with_gssapi:
                configure_args.append("--with-gss_impl=mit")
            else:
                configure_args.append("--disable-gssapi")

            if not self.options.with_plain:
                configure_args.append("--disable-plain")

            if not self.options.with_anon:
                configure_args.append("--disable-anon")

            if (
                self.options.with_postgresql
                or self.options.with_mysql
                or self.options.with_sqlite3
            ):
                configure_args.append("--enable-sql")
                if self.options.with_postgresql:
                    configure_args.append(
                        "--with-pgsql={}".format(self.deps_cpp_info["libpq"].rootpath)
                    )
                else:
                    configure_args.append("--with-pgsql=no")
                if self.options.with_mysql:
                    configure_args.append(
                        "--with-mysql={}".format(
                            self.deps_cpp_info["libmysqlclient"].rootpath
                        )
                    )
                else:
                    configure_args.append("--with-mysql=no")
                configure_args.append("--with-sqlite=no")
                if self.options.with_mysql:
                    configure_args.append(
                        "--with-sqlite3={}".format(
                            self.deps_cpp_info["libmysqlclient"].rootpath
                        )
                    )
                else:
                    configure_args.append("--with-sqlite3=no")
            else:
                configure_args.append("--disable-sql")

            configure_file_path = os.path.join(self._source_subfolder)
            self._autotools.configure(
                configure_dir=configure_file_path, args=configure_args
            )
        return self._autotools

    def build(self):
        self._patch_sources()
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()

        self._remove_la()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def _remove_la(self):
        la_exp = os.path.join(self.package_folder, "lib", "**", "*.la")
        for la_file in glob.glob(la_exp, recursive=True):
            os.remove(la_file)

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libsasl2"
        self.cpp_info.libs = ["sasl2"]
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
