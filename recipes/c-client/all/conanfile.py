import os
import stat

from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.43.0"


class CclientConan(ConanFile):
    name = "c-client"
    description = "University of Washington IMAP toolkit"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/uw-imap/imap"
    topics = "imap", "uw-imap", "tcp-ip"
    license = "Apache-2.0"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }
    exports_sources = "patches/*"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _is_msvc(self):
        return self._settings_build.compiler in ("Visual Studio", "msvc")

    def validate(self):
        if self._settings_build.os == "Windows" and not self._is_msvc:
            raise ConanInvalidConfiguration(
                "c-client is setup to build only with MSVC on Windows"
            )
        # FIXME: need krb5 recipe
        if self.settings.os == "Macos":
            raise ConanInvalidConfiguration(
                "c-client depends on krb5 on MacOS and it's not packaged by "
                "Conan yet"
            )

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if not self._is_msvc:
            self.requires("openssl/1.1.1q")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _patch_msvc(self):
        opt_flags = "/O2 /Ob2 /DNDEBUG"
        if self.settings.build_type == "Debug":
            opt_flags = "/Zi /Ob0 /Od /RTC1"
        runtime = f"/{self.settings.compiler.runtime}"
        # NOTE: boatloads of warnings for truncation, sign mismatch,
        #       implicit conversions, just the usual C things
        warnings = \
            "/W3 /wd4267 /wd4244 /wd4273 /wd4311 /wd4312 /wd4133 /wd4028"
        cflags = f"{runtime} {warnings} /GS {opt_flags}"
        search = "EXTRACFLAGS ="
        replace = f"EXTRACFLAGS = {cflags}"
        tools.replace_in_file(r"src\osdep\nt\makefile.w2k", search, replace)

    def _build_msvc(self):
        make = "nmake /nologo /f makefile.w2k"
        with tools.vcvars(self):
            self.run(f"{make} c-client", run_environment=True)
            self.run(make, cwd="c-client", run_environment=True)

    def _chmod_x(self, path):
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)

    def _touch(self, path):
        with open(path, "a", encoding=None): pass

    def _build_unix(self):
        self._touch("ip6")
        self._chmod_x("tools/an")
        self._chmod_x("tools/ua")
        unix = "src/osdep/unix"
        self._chmod_x(f"{unix}/drivers")
        self._chmod_x(f"{unix}/mkauths")
        search = "SSLDIR=/usr/local/ssl"
        ssldir = self.deps_cpp_info["openssl"].rootpath
        tools.replace_in_file(f"{unix}/Makefile", search, f"SSLDIR={ssldir}")
        # This is from the Homebrew Formula
        tools.replace_in_file(
            "src/osdep/unix/ssl_unix.c",
            "#include <x509v3.h>\n#include <ssl.h>",
            "#include <ssl.h>\n#include <x509v3.h>"
        )
        target = "osx" if self.settings.os == "Macos" else "slx"
        # NOTE: only one job is used, because there are issues with dependency
        #       tracking in parallel builds
        args = ["IP=6", "-j1"]
        AutoToolsBuildEnvironment(self).make(target=target, args=args)

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        if self._is_msvc:
            self._patch_msvc()
            self._build_msvc()
        else:
            self._build_unix()

    def package(self):
        self.copy("LICENSE.txt", "licenses")
        self.copy("c-client/*.h", "include")
        if self._is_msvc:
            self.copy("*.lib", "lib", "c-client")
        else:
            self.copy("*.a", "lib", "c-client")

    def package_info(self):
        if self._is_msvc:
            self.cpp_info.system_libs = \
                ["Winmm", "Ws2_32", "Secur32", "Crypt32"]
        else:
            self.cpp_info.defines = ["_DEFAULT_SOURCE"]
            self.cpp_info.system_libs = ["crypt"]
            self.cpp_info.requires = ["openssl::crypto", "openssl::ssl"]
        self.cpp_info.libs = ["cclient" if self._is_msvc else "c-client"]
