from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import contextlib
import os


required_conan_version = ">=1.33.0"


class WolfSSLConan(ConanFile):
    name = "wolfssl"
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.wolfssl.com/"
    description = "wolfSSL (formerly CyaSSL) is a small, fast, portable implementation of TLS/SSL for embedded devices to the cloud."
    topics = ("wolfssl", "tls", "ssl", "iot", "fips", "secure", "cryptology", "secret")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "opensslextra": [True, False],
        "opensslall": [True, False],
        "sslv3": [True, False],
        "alpn": [True, False],
        "des3": [True, False],
        "tls13": [True, False],
        "certgen": [True, False],
        "dsa": [True, False],
        "ripemd": [True, False],
        "sessioncerts": [True, False],
        "sni": [True, False],
        "testcert": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "opensslextra": False,
        "opensslall": False,
        "sslv3": False,
        "alpn": False,
        "des3": False,
        "tls13": False,
        "certgen": False,
        "dsa": False,
        "ripemd": False,
        "sessioncerts": False,
        "sni": False,
        "testcert": False,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        self.build_requires("libtool/2.4.6")

    def validate(self):
        if self.options.opensslall and not self.options.opensslextra:
            raise ConanInvalidConfiguration("The option 'opensslall' requires 'opensslextra=True'")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self):
                env = {
                    "CC": "{} cl -nolink".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                    "CXX": "{} cl -nolink".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                    "AR": "{} lib".format(tools.unix_path(self.deps_user_info["automake"].ar_lib)),
                    "LD": "{} cl -nolink".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        if self.settings.compiler == "Visual Studio":
            self._autotools.link_flags.append("-ladvapi32")
        self._autotools.libs = []
        if self.settings.compiler == "Visual Studio":
            self._autotools.flags.append("-FS")
        yes_no = lambda v: "yes" if v else "no"
        conf_args = [
            "--disable-examples",
            "--disable-crypttests",
            "--enable-harden",
            "--enable-debug={}".format(yes_no(self.settings.build_type == "Debug")),
            "--enable-opensslall={}".format(yes_no(self.options.opensslall)),
            "--enable-opensslextra={}".format(yes_no(self.options.opensslextra)),
            "--enable-sslv3={}".format(yes_no(self.options.sslv3)),
            "--enable-alpn={}".format(yes_no(self.options.alpn)),
            "--enable-des3={}".format(yes_no(self.options.des3)),
            "--enable-tls13={}".format(yes_no(self.options.tls13)),
            "--enable-certgen={}".format(yes_no(self.options.certgen)),
            "--enable-dsa={}".format(yes_no(self.options.dsa)),
            "--enable-ripemd={}".format(yes_no(self.options.ripemd)),
            "--enable-sessioncerts={}".format(yes_no(self.options.sessioncerts)),
            "--enable-sni={}".format(yes_no(self.options.sni)),
            "--enable-testcert={}".format(yes_no(self.options.testcert)),
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        with tools.chdir(self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)
        with self._build_context():
            autotools = self._configure_autotools()
            if self.settings.compiler == "Visual Studio" and (tools.Version(self.version) < "4.7" or self.version == "5.0.0"):
                tools.replace_in_file("libtool",
                                      "AR_FLAGS=\"Ucru\"", "AR_FLAGS=\"cru\"")
            autotools.make()

    def package(self):
        self.copy(pattern="LICENSING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()
        os.unlink(os.path.join(self.package_folder, "bin", "wolfssl-config"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            tools.rename(os.path.join(self.package_folder, "lib", "wolfssl.dll.lib"),
                         os.path.join(self.package_folder, "lib", "wolfssl.lib"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "wolfssl"
        libname = "wolfssl"
        self.cpp_info.libs = [libname]
        if self.options.shared:
            self.cpp_info.defines.append("WOLFSSL_DLL")
        if not self.options.shared:
            if self.settings.os == "Linux":
                self.cpp_info.system_libs.append("m")
            elif self.settings.os == "Windows":
                self.cpp_info.system_libs.extend(["advapi32", "ws2_32"])
