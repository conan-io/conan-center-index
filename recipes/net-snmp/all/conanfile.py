import os
import stat

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir, chdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, msvc_runtime_flag, NMakeToolchain
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name

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
        self.requires("openssl/[>=1.1 <4]")
        self.requires("pcre/8.45")
        self.requires("zlib/[>=1.2.11 <2]")

    def validate(self):
        if is_msvc(self) and self.options.shared:
            # FIXME: Linker errors against third-party dependencies:
            # snmp_openssl.obj : error LNK2019: unresolved external symbol CRYPTO_free referenced in function _extract_oname
            raise ConanInvalidConfiguration(f"{self.ref} fails when building as shared library, use -o '&:shared=False'. Contributions are welcome!")

    def build_requirements(self):
        if is_msvc(self):
            self.tool_requires("strawberryperl/5.32.1.1")
        else:
            self.tool_requires("gnu-config/cci.20210814")
            self.tool_requires("autoconf/2.71")
            self.tool_requires("automake/1.16.5")
            self.tool_requires("libtool/2.4.7")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.2.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _is_debug(self):
        return self.settings.build_type == "Debug"

    def generate(self):
        if is_msvc(self):
            tc = NMakeToolchain(self)
            tc.generate()
            # Workaround for "unresolved external symbol" errors during shared build
            env = VirtualRunEnv(self)
            env.generate(scope="build")
        else:
            if not cross_building(self):
                env = VirtualRunEnv(self)
                env.generate(scope="build")
            tc = AutotoolsToolchain(self)
            debug_flag = "enable" if self._is_debug else "disable"
            ipv6_flag = "enable" if self.options.with_ipv6 else "disable"
            openssl_path = self.dependencies["openssl"].package_folder
            zlib_path = self.dependencies["zlib"].package_folder
            tc.configure_args += [
                f"--with-openssl={openssl_path}",
                f"--with-zlib={zlib_path}",
                f"--{debug_flag}-debugging",
                f"--{ipv6_flag}-ipv6",
                "--with-defaults",
                "--without-rpm",
                "--without-pcre",
                "--disable-agent",
                "--disable-applications",
                "--disable-manuals",
                "--disable-scripts",
                "--disable-mibs",
                "--disable-embedded-perl",
            ]
            if self.settings.os in ["Linux"]:
                tc.extra_ldflags.append("-ldl")
                tc.extra_ldflags.append("-lpthread")
            tc.generate()

            deps = AutotoolsDeps(self)
            deps.generate()

            deps = PkgConfigDeps(self)
            deps.generate()

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
            replace_in_file(self, "build.pl", search, replace)
        replace_in_file(self, "Configure", '"/runtime', f'"/{msvc_runtime_flag(self)}')
        link_lines = "\n".join(
            f'#    pragma comment(lib, "{lib}.lib")'
            for lib in ssl_info.cpp_info.libs + ssl_info.cpp_info.system_libs
        )
        config = r"net-snmp\net-snmp-config.h.in"
        replace_in_file(self, config, "/* Conan: system_libs */", link_lines)

    def _patch_unix(self):
        for gnu_config in [
            self.conf.get("user.gnu-config:config_guess", check_type=str),
            self.conf.get("user.gnu-config:config_sub", check_type=str),
        ]:
            if gnu_config:
                copy(self, os.path.basename(gnu_config), src=os.path.dirname(gnu_config), dst=self.source_folder)
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

    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            with chdir(self, os.path.join(self.source_folder, "win32")):
                self._patch_msvc()
                self.run("perl build.pl")
                self.run("nmake /nologo libsnmp")
        else:
            self._patch_unix()
            configure_path = os.path.join(self.source_folder, "configure")
            os.chmod(configure_path, os.stat(configure_path).st_mode | stat.S_IEXEC)
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            autotools.make(target="snmplib", args=["NOAUTODEPS=1"])

    def package(self):
        copy(self, "COPYING",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        if is_msvc(self):
            cfg = "debug" if self._is_debug else "release"
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
        else:
            autotools = Autotools(self)
            #only install with -j1 as parallel install will break dependencies. Probably a bug in the dependencies
            #install specific targets instead of just everything as it will try to do perl stuff on you host machine
            autotools.install(args=["-j1"], target="installsubdirs installlibs installprogs installheaders")
            rm(self, "README", self.package_folder, recursive=True)
            rmdir(self, os.path.join(self.package_folder, "bin"))
            rm(self, "*.la", self.package_folder, recursive=True)
            fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["netsnmp"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["rt", "pthread", "m"])
        if is_apple_os(self):
            self.cpp_info.frameworks.extend(["CoreFoundation", "DiskArbitration", "IOKit"])
