import functools
import os
import stat

from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.43.0"


class CclientConan(ConanFile):
    name = "c-client"
    description = "University of Washington IMAP toolkit"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/uw-imap/imap"
    topics = ("imap",)
    license = "Apache-2.0"
    settings = ("os", "arch", "compiler", "build_type")
    options = {
        # FIXME: can this library be made shared?
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }
    exports_sources = ("patches/*", "cclient.def")

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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if not self._is_msvc:
            self.requires("openssl/1.1.1m")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True)

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
        # FIXME: use link.exe with cclient.def for shared build
        # NOTE: the makefile depends on cclient.lib, which is generated for all
        #       library types anyway
        link = "LIB /NOLOGO /OUT:cclient.lib"
        search = "EXTRACFLAGS =\nLINK ="
        replace = f"EXTRACFLAGS = {cflags}\nLINK = {link}"
        tools.replace_in_file(r"src\osdep\nt\makefile.w2k", search, replace)

    def _build_msvc(self):
        make = "nmake /nologo /f makefile.w2k"
        with tools.vcvars(self):
            self.run(f"{make} c-client")
            self.run(make, cwd="c-client")

    def _chmod_x(self, path):
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)

    def _build_unix(self):
        target = "osx" if self.settings.os == "Macos" else "slx"
        with open("ip6", "a"): pass
        with open("OSTYPE", "w") as f: f.write(f"{target}\n")
        self._chmod_x("tools/an")
        self._chmod_x("tools/ua")
        unix = "src/osdep/unix"
        self._chmod_x(f"{unix}/drivers")
        self._chmod_x(f"{unix}/mkauths")
        search = "SSLDIR=/usr/local/ssl"
        ssldir = self.deps_cpp_info["openssl"].rootpath
        tools.replace_in_file(f"{unix}/Makefile", search, f"SSLDIR={ssldir}")
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
        if self._is_msvc:
            self.copy("c-client/*.h", "include")
            self.copy("*.lib", "lib", "c-client")
        else:
            self.copy("c-client/*.h", "include")
            self.copy("*.a", "lib", "c-client")

    def package_info(self):
        if self._is_msvc: # and not self.options.shared:
            self.cpp_info.system_libs = \
                ["Winmm", "Ws2_32", "Secur32", "Crypt32"]
        else:
            self.cpp_info.defines = ["_DEFAULT_SOURCE"]
            self.cpp_info.system_libs = ["crypt"]
        self.cpp_info.libs = ["cclient" if self._is_msvc else "c-client"]
