from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import functools
import os
import shutil

required_conan_version = ">=1.36.0"


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
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/1.1.1q")
        if self.options.with_postgresql:
            self.requires("libpq/14.2")
        if self.options.with_mysql:
            self.requires("libmysqlclient/8.0.29")
        if self.options.with_sqlite3:
            self.requires("sqlite3/3.39.2")
        if self.options.with_gssapi:
            raise ConanInvalidConfiguration("with_gssapi requires krb5 recipe, not yet available in CCI")
            self.requires("krb5/1.18.3")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(
                "Cyrus SASL package is not compatible with Windows yet."
            )

    def build_requirements(self):
        self.build_requires("gnu-config/cci.20210814")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB,
                    os.path.join(self._source_subfolder, "config", "config.sub"))
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS,
                    os.path.join(self._source_subfolder, "config", "config.guess"))

        configure = os.path.join(self._source_subfolder, "configure")
        # relocatable shared libs on macOS
        tools.files.replace_in_file(self, configure, "-install_name \\$rpath/", "-install_name @rpath/")
        # avoid SIP issues on macOS when dependencies are shared
        if tools.apple.is_apple_os(self):
            libpaths = ":".join(self.deps_cpp_info.lib_paths)
            tools.files.replace_in_file(self, 
                configure,
                "#! /bin/sh\n",
                "#! /bin/sh\nexport DYLD_LIBRARY_PATH={}:$DYLD_LIBRARY_PATH\n".format(libpaths),
            )

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)

        yes_no = lambda v: "yes" if v else "no"
        rootpath = lambda req: tools.microsoft.unix_path(self, self.deps_cpp_info[req].rootpath)
        rootpath_no = lambda v, req: rootpath(req) if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
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
        ]
        if self.options.with_gssapi:
            args.append("--with-gss_impl=mit")

        autotools.configure(configure_dir=self._source_subfolder, args=args)
        return autotools

    def build(self):
        self._patch_sources()
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rm(self, "*.la", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libsasl2")
        self.cpp_info.libs = ["sasl2"]

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        # TODO: to remove in conan v2 once pkg_config generator removed
        self.cpp_info.names["pkg_config"] = "libsasl2"
