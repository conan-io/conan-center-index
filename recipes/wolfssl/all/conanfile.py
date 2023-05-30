from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rename, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import check_min_vs, is_msvc, unix_path
import os

required_conan_version = ">=1.54.0"


class WolfSSLConan(ConanFile):
    name = "wolfssl"
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.wolfssl.com/"
    description = (
        "wolfSSL (formerly CyaSSL) is a small, fast, portable implementation "
        "of TLS/SSL for embedded devices to the cloud."
    )
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

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
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
            "--enable-tls13={}".format(yes_no(self.options.tls13)),
            "--enable-certgen={}".format(yes_no(self.options.certgen)),
            "--enable-dsa={}".format(yes_no(self.options.dsa)),
            "--enable-ripemd={}".format(yes_no(self.options.ripemd)),
            "--enable-sessioncerts={}".format(yes_no(self.options.sessioncerts)),
            "--enable-sni={}".format(yes_no(self.options.sni)),
            "--enable-testcert={}".format(yes_no(self.options.testcert)),
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ])
        if is_msvc(self):
            tc.extra_ldflags.append("-ladvapi32")
            if check_min_vs(self, "180", raise_invalid=False):
                tc.extra_cflags.append("-FS")
        env = tc.environment()
        if is_msvc(self):
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
        if is_msvc(self) and self.options.shared:
            rename(self, os.path.join(self.package_folder, "lib", "wolfssl.dll.lib"),
                         os.path.join(self.package_folder, "lib", "wolfssl.lib"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "wolfssl")
        self.cpp_info.libs = ["wolfssl"]
        if self.options.shared:
            self.cpp_info.defines.append("WOLFSSL_DLL")
        if not self.options.shared:
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.extend(["m", "pthread"])
            elif self.settings.os == "Windows":
                self.cpp_info.system_libs.extend(["advapi32", "ws2_32", "crypt32"])
            elif is_apple_os(self):
                self.cpp_info.frameworks.extend(["CoreFoundation", "Security"])
