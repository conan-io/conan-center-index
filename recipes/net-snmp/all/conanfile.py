import functools
import os
import stat
from contextlib import contextmanager

from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration

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
    topics = ("snmp",)
    license = "BSD-3-Clause"
    settings = ("os", "arch", "compiler", "build_type")
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
    requires = ("openssl/1.1.1m",)
    exports_sources = ("patches/*",)

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _is_msvc(self):
        return self._settings_build.compiler == "Visual Studio"

    @property
    def _is_debug(self):
        return self.settings.build_type == "Debug"

    def validate(self):
        if self._settings_build.os == "Windows" \
                and self._settings_build.compiler == "gcc":
            raise ConanInvalidConfiguration(
                "net-snmp is not setup to build with gcc on Windows yet"
            )

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True)

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

    @contextmanager
    def _add_write_permissions(self, file):
        write = stat.S_IWRITE
        saved_permissions = os.stat(file).st_mode
        if saved_permissions & write == write:
            yield
            return
        try:
            os.chmod(file, saved_permissions | write)
            yield
        finally:
            os.chmod(file, saved_permissions)

    @contextmanager
    def _replace_in_file(self, file):
        with self._add_write_permissions(file):
            with open(file, "r+", encoding="utf-8") as f:
                args = [f.read()]

                def replacer(search, replace):
                    args[0] = args[0].replace(search, replace, 1)

                yield replacer
                f.seek(0)
                f.write(*args)
                f.truncate()

    def _patch_msvc(self):
        ssl_info = self.deps_cpp_info["openssl"]
        openssl_root = ssl_info.rootpath.replace("\\", "/")
        with self._replace_in_file("win32\\build.pl") as replacer:
            replacer("$openssl = false", "$openssl = true")
            replacer(
                r'$default_openssldir . "\\include"',
                f'"{openssl_root}/include"'
            )
            replacer(
                r'$default_openssldir . "\\lib\\VC"',
                f'"{openssl_root}/lib"'
            )
            if self._is_debug:
                replacer("$debug = false", "$debug = true")
            if self.options.shared:
                replacer("$link_dynamic = false", "$link_dynamic = true")
            if self.options.with_ipv6:
                replacer("$b_ipv6 = false", "$b_ipv6 = true")
        tools.replace_in_file(
            "win32\\Configure",
            '"/MDd' if self._is_debug else '"/MD',
            f'"/{self.settings.compiler.runtime}'
        )
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
        autotools.configure(args=args)
        return autotools

    def _patch_unix(self):
        crypto_libs = self.deps_cpp_info["openssl"].system_libs
        if len(crypto_libs) != 0:
            crypto_link_flags = " -l".join(crypto_libs)
            tools.replace_in_file(
                "configure",
                'LIBCRYPTO="-l${CRYPTO}"',
                'LIBCRYPTO="-l${CRYPTO} -l%s"' % (crypto_link_flags,)
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
        for dir in ["", "agent/", "library/"]:
            self.copy(f"net-snmp/{dir}*.h", "include", "win32")
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
        name = "netsnmp"
        info = self.cpp_info

        info.set_property("cmake_file_name", name)
        info.set_property("cmake_target_name", f"{name}::{name}")

        info.names.update({
            "cmake_find_package": name,
            "cmake_find_package_multi": name,
        })

        info.libs = [name]
