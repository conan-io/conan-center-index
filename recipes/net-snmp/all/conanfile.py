import functools
import os
import stat

from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.43.0"


class NetSnmpConan(ConanFile):
    name = "net-snmp"
    description = (
        "Simple Network Management Protocol (SNMP) is a widely used protocol "
        "for monitoring the health and welfare of network equipment "
        "(eg. routers), computer equipment and even devices like UPSs."
    )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.net-snmp.org/"
    topics = "snmp"
    license = "BSD-3-Clause"
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
    requires = "openssl/1.1.1m"
    exports_sources = "patches/*"

    @property
    def _is_msvc(self):
        return self.settings.compiler in ("Visual Studio", "msvc")

    def validate(self):
        if self.settings.os == "Windows" and not self._is_msvc:
            raise ConanInvalidConfiguration(
                "net-snmp is setup to build only with MSVC on Windows"
            )

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if self._is_msvc:
            self.build_requires("strawberryperl/5.30.0.1")

    @property
    def _is_debug(self):
        return self.settings.build_type == "Debug"

    def _patch_msvc(self):
        ssl_info = self.deps_cpp_info["openssl"]
        openssl_root = ssl_info.rootpath.replace("\\", "/")
        search_replace = [
            (
                r'$default_openssldir . "\\include"',
                f"'{openssl_root}/include'"
            ),
            (r'$default_openssldir . "\\lib\\VC"', f"'{openssl_root}/lib'"),
            ("$openssl = false", "$openssl = true")
        ]
        if self._is_debug:
            search_replace.append(("$debug = false", "$debug = true"))
        if self.options.shared:
            search_replace.append((
                "$link_dynamic = false",
                "$link_dynamic = true"
            ))
        if self.options.with_ipv6:
            search_replace.append(("$b_ipv6 = false", "$b_ipv6 = true"))
        for search, replace in search_replace:
            tools.replace_in_file("win32\\build.pl", search, replace)
        runtime = self.settings.compiler.runtime
        tools.replace_in_file("win32\\Configure", '"/runtime', f'"/{runtime}')
        link_lines = "\n".join(
            f'#    pragma comment(lib, "{lib}.lib")'
            for lib in ssl_info.libs + ssl_info.system_libs
        )
        config = r"win32\net-snmp\net-snmp-config.h.in"
        tools.replace_in_file(config, "/* Conan: system_libs */", link_lines)

    def _build_msvc(self):
        if self.should_configure:
            self._patch_msvc()
            self.run("perl build.pl", cwd="win32")
        if self.should_build:
            with tools.vcvars(self):
                self.run("nmake /nologo libsnmp", cwd="win32")

    @functools.lru_cache(1)
    def _configure_autotools(self):
        disabled_link_type = "static" if self.options.shared else "shared"
        debug_flag = "enable" if self._is_debug else "disable"
        ipv6_flag = "enable" if self.options.with_ipv6 else "disable"
        ssl_path = self.deps_cpp_info["openssl"].rootpath
        args = [
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
        autotools = AutoToolsBuildEnvironment(self)
        autotools.libs = []
        autotools.configure(args=args)
        return autotools

    def _patch_unix(self):
        tools.replace_in_file(
            "configure",
            "-install_name \\$rpath/",
            "-install_name @rpath/"
        )
        crypto_libs = self.deps_cpp_info["openssl"].system_libs
        if len(crypto_libs) != 0:
            crypto_link_flags = " -l".join(crypto_libs)
            tools.replace_in_file(
                "configure",
                'LIBCRYPTO="-l${CRYPTO}"',
                'LIBCRYPTO="-l${CRYPTO} -l%s"' % (crypto_link_flags,)
            )
            tools.replace_in_file(
                "configure",
                'LIBS="-lcrypto  $LIBS"',
                f'LIBS="-lcrypto -l{crypto_link_flags} $LIBS"'
            )

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        if self._is_msvc:
            self._build_msvc()
        else:
            self._patch_unix()
            os.chmod("configure", os.stat("configure").st_mode | stat.S_IEXEC)
            self._configure_autotools()\
                .make(target="snmplib", args=["NOAUTODEPS=1"])

    def _package_msvc(self):
        cfg = "debug" if self._is_debug else "release"
        self.copy("netsnmp.dll", "bin", fr"win32\bin\{cfg}")
        self.copy("netsnmp.lib", "lib", fr"win32\lib\{cfg}")
        self.copy("include/net-snmp/*.h")
        for directory in ["", "agent/", "library/"]:
            self.copy(f"net-snmp/{directory}*.h", "include", "win32")
        self.copy("COPYING", "licenses")

    def _remove(self, path):
        if os.path.isdir(path):
            tools.rmdir(path)
        else:
            os.remove(path)

    def _package_unix(self):
        self._configure_autotools().install(args=["NOAUTODEPS=1"])
        tools.remove_files_by_mask(self.package_folder, "README")
        tools.rmdir(os.path.join(self.package_folder, "bin"))
        lib_dir = os.path.join(self.package_folder, "lib")
        for entry in os.listdir(lib_dir):
            if not entry.startswith("libnetsnmp.") or entry.endswith(".la"):
                self._remove(os.path.join(lib_dir, entry))
        self.copy("COPYING", "licenses")

    def package(self):
        if self._is_msvc:
            self._package_msvc()
        else:
            self._package_unix()

    def package_info(self):
        self.cpp_info.libs = ["netsnmp"]
        self.cpp_info.requires = ["openssl::openssl"]
