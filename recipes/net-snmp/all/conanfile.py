import os
import stat
import textwrap

from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.env import VirtualRunEnv
from conan.tools.files import copy, get, replace_in_file, rm, rmdir, chdir
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
        self.requires("openssl/[>=1.1 <4]", transitive_headers=True)
        self.requires("pcre/8.45")
        self.requires("zlib/[>=1.2.11 <2]")

    def build_requirements(self):
        if is_msvc(self):
            self.tool_requires("strawberryperl/5.32.1.1")
        else:
            self.tool_requires("gnu-config/cci.20210814")
            self.tool_requires("autoconf/2.71")
            self.tool_requires("automake/1.16.5")
            self.tool_requires("libtool/2.4.7")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2.0 <3]")

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

    def _configure_msvc(self):
        ssl = self.dependencies["openssl"].package_folder.replace("\\", "/")
        prefix = self.package_folder.replace("\\", "/")
        args = [
            "perl", "Configure",
            f"--config={'debug' if self._is_debug else 'release'}",
            f"--linktype={'dynamic' if self.options.shared else 'static'}",
            "--with-ssl",
            f'--with-sslincdir="{ssl}/include"',
            f'--with-ssllibdir="{ssl}/lib"',
            f'--prefix="{prefix}"',
        ]
        if self.options.with_ipv6:
            args.append("--with-ipv6")
        self.run(" ".join(args))

    def _patch_msvc(self):
        # net-snmp version-independent patching, instead of using patch files
        if "MT" in msvc_runtime_flag(self):
            replace_in_file(self, "Configure", "/MD", "/MT", strict=False)
        ssl_info = self.dependencies["openssl"].cpp_info
        zlib_info = self.dependencies["zlib"].cpp_info
        extra_libs = zlib_info.libs + \
            ssl_info.components["ssl"].libs + ssl_info.components["ssl"].system_libs + \
            ssl_info.components["crypto"].libs + ssl_info.components["crypto"].system_libs
        replace_in_file(self,
                        os.path.join("net-snmp", "net-snmp-config.h.in"),
                        textwrap.dedent("""\
                            #    ifdef _DLL
                            #      pragma comment(lib, "libcrypto.lib")
                            #      pragma comment(lib, "libssl.lib")
                            #    else
                            #      pragma comment(lib, "libcrypto_static.lib")
                            #      pragma comment(lib, "libssl_static.lib")
                            #    endif"""
                        ),
                        "\n".join(f'#    pragma comment(lib, "{lib}.lib")' for lib in extra_libs))
        if self.options.shared:
            replace_in_file(self,
                            os.path.join("libsnmp_dll", "Makefile.in"),
                            "LINK32_FLAGS=advapi32.lib ws2_32.lib kernel32.lib user32.lib",
                            "LINK32_FLAGS=" + " ".join(f"{lib}.lib" for lib in extra_libs) + \
                                ' /libpath:"{}"'.format(zlib_info.libdirs[0].replace("\\", "/")))

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

    def build(self):
        if is_msvc(self):
            with chdir(self, os.path.join(self.source_folder, "win32")):
                self._patch_msvc()
                self._configure_msvc()
                self.run("nmake /nologo libsnmp")
        else:
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
            if self.options.shared:
                copy(self, "netsnmp.dll",
                     dst=os.path.join(self.package_folder, "bin"),
                     src=os.path.join(self.source_folder, rf"win32\bin\{cfg}"))
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
            for lib in ["libnetsnmpagent", "libnetsnmpmibs", "libnetsnmphelpers"]:
                rm(self, f"{lib}.*", os.path.join(self.package_folder, "lib"))
            fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["netsnmp"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["rt", "pthread", "m"])
        if is_apple_os(self):
            self.cpp_info.frameworks.extend(["CoreFoundation", "DiskArbitration", "IOKit"])
