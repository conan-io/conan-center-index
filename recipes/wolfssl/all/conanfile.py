from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rename, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import check_min_vs, is_msvc, unix_path
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class WolfSSLConan(ConanFile):
    name = "wolfssl"
    description = (
        "wolfSSL (formerly CyaSSL) is a small, fast, portable implementation "
        "of TLS/SSL for embedded devices to the cloud."
    )
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.wolfssl.com/"
    topics = ("wolfssl", "tls", "ssl", "iot", "fips", "secure", "cryptology", "secret")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
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
        "with_curl": [True, False],
        "with_quic": [True, False],
        "with_experimental": [True, False],
        "with_rpk": [True, False],
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
        "with_curl": False,
        "with_quic": False,
        "with_experimental": False,
        "with_rpk": False,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "5.2.0":
            del self.options.with_curl
        if Version(self.version) < "5.5.0":
            del self.options.with_quic
        if Version(self.version) < "5.7.0":
            del self.options.with_experimental
        if Version(self.version) < "5.7.2":
            del self.options.with_rpk
        if self.settings.os == "baremetal":
            del self.options.shared
            self.package_type = "static-library"

    def configure(self):
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.options.opensslall and not self.options.opensslextra:
            raise ConanInvalidConfiguration("The option 'opensslall' requires 'opensslextra=True'")

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")
        self.tool_requires("cmake/[>=3.22 <4]")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args.extend([
            "--disable-examples",
            "--disable-crypttests",
            "--enable-harden",
            "--enable-debug={}".format(yes_no(self.settings.build_type == "Debug")),
            "--enable-opensslall={}".format(yes_no(self.options.opensslall)),
            "--enable-opensslextra={}".format(yes_no(self.options.opensslextra)),
            "--enable-sslv3={}".format(yes_no(self.options.sslv3)),
            "--enable-alpn={}".format(yes_no(self.options.alpn)),
            "--enable-des3={}".format(yes_no(self.options.des3)),
            "--enable-tls13={}".format(yes_no(self.options.tls13 or self.options.get_safe("with_quic"))),
            "--enable-certgen={}".format(yes_no(self.options.certgen)),
            "--enable-dsa={}".format(yes_no(self.options.dsa)),
            "--enable-ripemd={}".format(yes_no(self.options.ripemd)),
            "--enable-sessioncerts={}".format(yes_no(self.options.sessioncerts)),
            "--enable-sni={}".format(yes_no(self.options.sni)),
            "--enable-testcert={}".format(yes_no(self.options.testcert)),
            "--enable-shared={}".format(yes_no(self.options.get_safe("shared"))),
            "--enable-static={}".format(yes_no(not self.options.get_safe("shared"))),
        ])
        if self.options.get_safe("with_curl"):
            tc.configure_args.append("--enable-curl")
        if self.options.get_safe("with_quic"):
            tc.configure_args.append("--enable-quic")
        if self.options.get_safe("with_experimental"):
            tc.configure_args.append("--enable-experimental")
        if self.options.get_safe("with_rpk"):
            tc.configure_args.append("--enable-rpk")
        if self.settings.os == "baremetal":
            # INFO: Disable filesystem to avoid error: #error "<dirent.h> not supported"
            tc.configure_args.append("--disable-filesystem")
            # INFO: Recommended for faster cryptographic operations, predictable memory usage, and enhanced security
            # See https://www.wolfssl.com/documentation/manuals/wolfssl/chapter02.html#building-with-configure-with-cross-compile
            tc.configure_args.append("--enable-fastmath")
            # INFO: Inject HAVE_PK_CALLBACKS, WOLFSSL_USER_IO, NO_WRITEV and TIME_T_NOT_64BIT
            tc.extra_defines.extend(self._defines)
        env = None
        if is_msvc(self):
            tc.extra_ldflags.append("-ladvapi32")
            if check_min_vs(self, "180", raise_invalid=False):
                tc.extra_cflags.append("-FS")
            env = tc.environment()
            automake_conf = self.dependencies.build["automake"].conf_info
            compile_wrapper = unix_path(self, automake_conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, automake_conf.get("user.automake:lib-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f"{ar_wrapper} lib")
        tc.generate(env)

    def build(self):
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "LICENSING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        os.unlink(os.path.join(self.package_folder, "bin", "wolfssl-config"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)
        if is_msvc(self) and self.options.get_safe("shared"):
            rename(self, os.path.join(self.package_folder, "lib", "wolfssl.dll.lib"),
                         os.path.join(self.package_folder, "lib", "wolfssl.lib"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "wolfssl")
        self.cpp_info.libs = ["wolfssl"]
        self.cpp_info.defines = self._defines
        if self.options.get_safe("shared"):
            self.cpp_info.defines.append("WOLFSSL_DLL")
        if not self.options.get_safe("shared"):
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.extend(["m", "pthread"])
            elif self.settings.os == "Windows":
                self.cpp_info.system_libs.extend(["advapi32", "ws2_32"])
                if Version(self.version) >= "5.6.0":
                    self.cpp_info.system_libs.append("crypt32")
            elif is_apple_os(self) and Version(self.version) >= "5.6.0":
                self.cpp_info.frameworks.extend(["CoreFoundation", "Security"])

    @property
    def _32bitarchs(self):
        return [
            "x86",
            "ppc32",
            "armv5el",
            "armv5hf",
            "armv6",
            "armv7",
            "armv7hf",
            "armv7s",
            "armv7k",
            "armv8_32",
            "mips",
            "s390",
        ]

    @property
    def _defines(self):
        # INFO: These defines are defined by autotools already when building,
        #       but they need to be forwarded to the consumers
        # See https://www.wolfssl.com/documentation/manuals/wolfssl/chapter02.html#building-with-configure-with-cross-compile
        defines = ["TFM_TIMING_RESISTANT", "ECC_TIMING_RESISTANT", "WC_RSA_BLINDING"]
        if self.settings.os == "baremetal":
            defines.extend([
                "NO_FILESYSTEM",
                "USE_FAST_MATH",
                "HAVE_PK_CALLBACKS",
                "WOLFSSL_USER_IO",
                "NO_WRITEV"
            ])
            if self.settings.arch in self._32bitarchs:
                defines.append("TIME_T_NOT_64BIT")
        return defines
