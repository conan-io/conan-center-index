import os
import stat

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, msvc_runtime_flag

required_conan_version = ">=1.53.0"


class NetSnmpConan(ConanFile):
    name = "net-snmp"
    description = (
        "Simple Network Management Protocol (SNMP) is a widely used protocol "
        "for monitoring the health and welfare of network equipment "
        "(eg. routers), computer equipment and even devices like UPSs."
    )
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.net-snmp.org/"
    topics = "snmp"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ipv6": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ipv6": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openssl/1.0.2u")

    def validate(self):
        if self.settings.os == "Windows" and not is_msvc(self):
            raise ConanInvalidConfiguration("net-snmp is setup to build only with MSVC on Windows")

    def build_requirements(self):
        if is_msvc(self):
            self.tool_requires("strawberryperl/5.32.1.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _is_debug(self):
        return self.settings.build_type == "Debug"

    def generate(self):
        disabled_link_type = "static" if self.options.shared else "shared"
        debug_flag = "enable" if self._is_debug else "disable"
        ipv6_flag = "enable" if self.options.with_ipv6 else "disable"
        ssl_path = self.dependencies["openssl"].package_folder
        tc = AutotoolsToolchain(self)
        tc.configure_args += [
            "--with-defaults",
            "--without-rpm",
            "--without-pcre",
            "--disable-agent",
            "--disable-applications",
            "--disable-manuals",
            "--disable-scripts",
            "--disable-mibs",
            "--disable-embedded-perl",
            f"--disable-{disabled_link_type}",
            f"--{debug_flag}-debugging",
            f"--{ipv6_flag}-ipv6",
            f"--with-openssl={ssl_path}",
        ]
        tc.generate()
        tc = AutotoolsDeps(self)
        tc.generate()

    def _patch_msvc(self):
        ssl_info = self.dependencies["openssl"]
        openssl_root = ssl_info.package_folder.replace("\\", "/")
        search_replace = [
            (r'$default_openssldir . "\\include"', f"'{openssl_root}/include'"),
            (r'$default_openssldir . "\\lib\\VC"', f"'{openssl_root}/lib'"),
            ("$openssl = false", "$openssl = true"),
        ]
        if self._is_debug:
            search_replace.append(("$debug = false", "$debug = true"))
        if self.options.shared:
            search_replace.append(("$link_dynamic = false", "$link_dynamic = true"))
        if self.options.with_ipv6:
            search_replace.append(("$b_ipv6 = false", "$b_ipv6 = true"))
        for search, replace in search_replace:
            replace_in_file(self, "win32\\build.pl", search, replace)
        runtime = msvc_runtime_flag(self)
        replace_in_file(self, "win32\\Configure", '"/runtime', f'"/{runtime}')
        link_lines = "\n".join(
            f'#    pragma comment(lib, "{lib}.lib")'
            for lib in ssl_info.cpp_info.libs + ssl_info.cpp_info.system_libs
        )
        config = r"win32\net-snmp\net-snmp-config.h.in"
        replace_in_file(self, config, "/* Conan: system_libs */", link_lines)

    def _build_msvc(self):
        if self.should_configure:
            self._patch_msvc()
            self.run("perl build.pl", cwd="win32")
        if self.should_build:
            autotools = Autotools(self)
            autotools.make(target="snmplib", args=["NOAUTODEPS=1"])

    def _patch_unix(self):
        configure_path = os.path.join(self.source_folder, "configure")
        replace_in_file(self, configure_path,
                        "-install_name \\$rpath/",
                        "-install_name @rpath/")
        crypto_libs = self.dependencies["openssl"].cpp_info.system_libs
        if len(crypto_libs) != 0:
            crypto_link_flags = " -l".join(crypto_libs)
            replace_in_file(self, configure_path,
                'LIBCRYPTO="-l${CRYPTO}"',
                'LIBCRYPTO="-l${CRYPTO} -l%s"' % (crypto_link_flags,))
            replace_in_file(self, configure_path,
                            'LIBS="-lcrypto  $LIBS"',
                            f'LIBS="-lcrypto -l{crypto_link_flags} $LIBS"')

    def _build_unix(self):
        self._patch_unix()
        configure_path = os.path.join(self.source_folder, "configure")
        os.chmod(configure_path, os.stat(configure_path).st_mode | stat.S_IEXEC)
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make(target="snmplib", args=["NOAUTODEPS=1"])

    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            self._build_msvc()
        else:
            self._build_unix()

    def _package_msvc(self):
        cfg = "debug" if self._is_debug else "release"
        copy(self, "netsnmp.dll",
             dst=os.path.join(self.package_folder, "bin"),
             src=os.path.join(self.source_folder, rf"win32\bin\{cfg}"))
        copy(self, "netsnmp.lib",
             dst=os.path.join(self.package_folder, "lib"),
             src=os.path.join(self.source_folder, rf"win32\lib\{cfg}"))
        copy(self, "include/net-snmp/*.h",
             dst=self.package_folder,
             src=self.source_folder)
        for directory in ["", "agent/", "library/"]:
            copy(self, f"net-snmp/{directory}*.h",
                 dst=os.path.join(self.package_folder, "include"),
                 src=os.path.join(self.source_folder, "win32"))
        copy(self, "COPYING",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)

    def _remove(self, path):
        if os.path.isdir(path):
            rmdir(self, path)
        else:
            os.remove(path)

    def _package_unix(self):
        autotools = Autotools(self)
        autotools.install(args=["NOAUTODEPS=1"])
        rm(self, "README", self.package_folder, recursive=True)
        rmdir(self, os.path.join(self.package_folder, "bin"))
        lib_dir = os.path.join(self.package_folder, "lib")
        for entry in os.listdir(lib_dir):
            if not entry.startswith("libnetsnmp.") or entry.endswith(".la"):
                self._remove(os.path.join(lib_dir, entry))
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=os.path.join(self.source_folder, "doc"))

    def package(self):
        if is_msvc(self):
            self._package_msvc()
        else:
            self._package_unix()

    def package_info(self):
        self.cpp_info.libs = ["netsnmp"]
