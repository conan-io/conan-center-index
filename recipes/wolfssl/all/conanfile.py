from conans import AutoToolsBuildEnvironment, ConanFile, tools
from contextlib import contextmanager
import os


class WolfSSLConan(ConanFile):
    name = "wolfssl"
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.wolfssl.com/"
    description = "wolfSSL (formerly CyaSSL) is a small, fast, portable implementation of TLS/SSL for embedded devices to the cloud."
    topics = ("conan", "wolfssl", "tls", "ssl", "iot", "fips", "secure", "cryptology", "secret")
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.opensslall and not self.options.opensslextra:
            raise ConanInvalidConfiguration("The option 'opensslall' requires 'opensslextra=True'")
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH") and \
                tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")
        self.build_requires("libtool/2.4.6")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}-stable".format(self.name, self.version), self._source_subfolder)

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
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
        conf_args = [
            "--disable-examples",
            "--disable-crypttests",
            "--enable-harden",
            "--enable-debug" if self.settings.build_type == "Debug" else "--disable-debug",
            "--enable-opensslall" if self.options.opensslall else "--disable-opensslall",
            "--enable-opensslextra" if self.options.opensslextra else "--disable-opensslextra",
            "--enable-sslv3" if self.options.sslv3 else "--disable-sslv3",
            "--enable-alpn" if self.options.alpn else "--disable-alpn",
            "--enable-des3" if self.options.des3 else "--disable-des3",
            "--enable-tls13" if self.options.tls13 else "--disable-tls13",
            "--enable-certgen" if self.options.certgen else "--disable-certgen",
            "--enable-dsa" if self.options.dsa else "--disable-dsa",
            "--enable-ripemd" if self.options.ripemd else "--disable-ripemd",
            "--enable-sessioncerts" if self.options.sessioncerts else "--disable-sessioncerts",
            "--enable-sni" if self.options.sni else "--disable-sni",
            "--enable-testcert" if self.options.testcert else "--disable-testcert",
        ]
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        with tools.chdir(self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)
        with self._build_context():
            autotools = self._configure_autotools()
            if self.settings.compiler == "Visual Studio":
                tools.replace_in_file("libtool",
                                      "AR_FLAGS=\"Ucru\"", "AR_FLAGS=\"cru\"")
            autotools.make()

    def package(self):
        self.copy(pattern="LICENSING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()
        os.unlink(os.path.join(self.package_folder, "bin", "wolfssl-config"))
        os.unlink(os.path.join(self.package_folder, "lib", "libwolfssl.la"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        libname = "wolfssl"
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            libname += ".dll.lib"
        self.cpp_info.libs = [libname]
        if self.options.shared:
            self.cpp_info.defines.append("WOLFSSL_DLL")
        if not self.options.shared:
            if self.settings.os == "Linux":
                self.cpp_info.system_libs.append("m")
            elif self.settings.os == "Windows":
                self.cpp_info.system_libs.extend(["advapi32", "ws2_32"])
