from conan import ConanFile, conan_version
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os, XCRun
from conan.tools.build import cross_building
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import (
    apply_conandata_patches, chdir, copy, export_conandata_patches,
    get, load, rename, replace_in_file, rm, rmdir, save
)
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, msvc_runtime_flag, unix_path
from conan.tools.scm import Version
from contextlib import contextmanager
from functools import total_ordering
import fnmatch
import json
import os
import textwrap

required_conan_version = ">=1.53.0"

@total_ordering
class OpenSSLVersion:
    def __init__(self, version):
        self._pre = ""
        version_str = str(version)

        tokens = version_str.split("-")
        if len(tokens) > 1:
            self._pre = tokens[1]
        version_str = tokens[0]

        tokens = version_str.split(".")
        self._major = int(tokens[0])
        self._minor = 0
        self._patch = 0
        self._build = ""
        if len(tokens) > 1:
            self._minor = int(tokens[1])
            if len(tokens) > 2:
                self._patch = tokens[2]
                if self._patch[-1].isalpha():
                    self._build = self._patch[-1]
                    self._patch = self._patch[:1]
                self._patch = int(self._patch)

    @property
    def base(self):
        return "%s.%s.%s" % (self._major, self._minor, self._patch)

    @property
    def as_list(self):
        return [self._major, self._minor, self._patch, self._build, self._pre]

    def __eq__(self, other):
        return self.compare(other) == 0

    def __lt__(self, other):
        return self.compare(other) == -1

    def __hash__(self):
        return hash(self.as_list)

    def compare(self, other):
        if not isinstance(other, OpenSSLVersion):
            other = OpenSSLVersion(other)
        if self.as_list == other.as_list:
            return 0
        if self.as_list < other.as_list:
            return -1
        else:
            return 1


class OpenSSLConan(ConanFile):
    name = "openssl"
    package_type = "library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/openssl/openssl"
    license = "OpenSSL"
    topics = ("openssl", "ssl", "tls", "encryption", "security")
    description = "A toolkit for the Transport Layer Security (TLS) and Secure Sockets Layer (SSL) protocols"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "no_threads": [True, False],
        "no_zlib": [True, False],
        "shared": [True, False],
        "fPIC": [True, False],
        "no_asm": [True, False],
        "enable_weak_ssl_ciphers": [True, False],
        "386": [True, False],
        "no_stdio": [True, False],
        "no_tests": [True, False],
        "no_sse2": [True, False],
        "no_bf": [True, False],
        "no_cast": [True, False],
        "no_des": [True, False],
        "no_dh": [True, False],
        "no_dsa": [True, False],
        "no_hmac": [True, False],
        "no_md2": [True, False],
        "no_md5": [True, False],
        "no_mdc2": [True, False],
        "no_rc2": [True, False],
        "no_rc4": [True, False],
        "no_rc5": [True, False],
        "no_rsa": [True, False],
        "no_sha": [True, False],
        "no_async": [True, False],
        "no_dso": [True, False],
        "no_aria": [True, False],
        "no_blake2": [True, False],
        "no_camellia": [True, False],
        "no_chacha": [True, False],
        "no_cms": [True, False],
        "no_comp": [True, False],
        "no_ct": [True, False],
        "no_deprecated": [True, False],
        "no_dgram": [True, False],
        "no_engine": [True, False],
        "no_filenames": [True, False],
        "no_gost": [True, False],
        "no_idea": [True, False],
        "no_md4": [True, False],
        "no_ocsp": [True, False],
        "no_pinshared": [True, False],
        "no_rmd160": [True, False],
        "no_sm2": [True, False],
        "no_sm3": [True, False],
        "no_sm4": [True, False],
        "no_srp": [True, False],
        "no_srtp": [True, False],
        "no_ssl": [True, False],
        "no_ts": [True, False],
        "no_whirlpool": [True, False],
        "no_ec": [True, False],
        "no_ecdh": [True, False],
        "no_ecdsa": [True, False],
        "no_rfc3779": [True, False],
        "no_seed": [True, False],
        "no_sock": [True, False],
        "no_ssl3": [True, False],
        "no_tls1": [True, False],
        "capieng_dialog": [True, False],
        "enable_capieng": [True, False],
        "openssldir": ["ANY", None]
    }
    default_options = {key: False for key in options.keys()}
    default_options["fPIC"] = True
    default_options["no_md2"] = True
    default_options["openssldir"] = None

    @property
    def _is_clangcl(self):
        return self.settings.compiler == "clang" and self.settings.os == "Windows"

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    @property
    def _use_nmake(self):
        return self._is_clangcl or is_msvc(self)

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _full_version(self):
        return OpenSSLVersion(self.version)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self._full_version >= "1.1.0":
            del self.options.no_md2
            del self.options.no_rc4
            del self.options.no_rc5
            del self.options.no_zlib

        if self._full_version < "1.1.0":
            del self.options.no_camellia
            del self.options.no_cast
            del self.options.no_cms
            del self.options.no_comp
            del self.options.no_dgram
            del self.options.no_engine
            del self.options.no_idea
            del self.options.no_md4
            del self.options.no_ocsp
            del self.options.no_seed
            del self.options.no_sock
            del self.options.no_srp
            del self.options.no_ts
            del self.options.no_whirlpool

        if self._full_version < "1.1.1":
            del self.options.no_aria
            del self.options.no_pinshared
            del self.options.no_sm2
            del self.options.no_sm3
            del self.options.no_sm4

        if self.settings.os != "Windows":
            del self.options.capieng_dialog
            del self.options.enable_capieng
        else:
            del self.options.fPIC

        if self.settings.os == "Emscripten":
            self.options.no_asm = True
            self.options.no_threads = True
            self.options.no_stdio = True
            self.options.no_tests = True

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self._full_version < "1.1.0" and not self.options.get_safe("no_zlib"):
            self.requires("zlib/1.2.13")

    def validate(self):
        if self.settings.os == "Emscripten":
            if not all((self.options.no_asm, self.options.no_threads, self.options.no_stdio, self.options.no_tests)):
                raise ConanInvalidConfiguration("os=Emscripten requires openssl:{no_asm,no_threads,no_stdio,no_tests}=True")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            if not self.options.no_asm:
                self.tool_requires("nasm/2.15.05")
            if self._use_nmake:
                self.tool_requires("strawberryperl/5.32.1.1")
            else:
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                    self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()

        tc = AutotoolsToolchain(self)
        # workaround for random error: size too large (archive member extends past the end of the file)
        # /Library/Developer/CommandLineTools/usr/bin/ar: internal ranlib command failed
        if self.settings.os == "Macos" and self._full_version < "1.1.0":
            tc.make_args = ["-j1"]
        # 1.1.0 era Makefiles don't do well with parallel installs
        if not self._use_nmake and self._full_version >= "1.1.0" and self._full_version < "1.1.1":
            tc.make_args = ["-j1"]
        if self.settings.os == "Macos" and not cross_building(self):
            tc.extra_cflags = [f"-isysroot {XCRun(self).sdk_path}"]
            tc.extra_cxxflags = [f"-isysroot {XCRun(self).sdk_path}"]
            tc.extra_ldflags = [f"-isysroot {XCRun(self).sdk_path}"]
        env = tc.environment()
        env.define("PERL", self._perl)
        tc.generate(env)
        gen_info = {}
        gen_info["CFLAGS"] = tc.cflags
        gen_info["CXXFLAGS"] = tc.cxxflags
        gen_info["DEFINES"] = tc.defines
        gen_info["LDFLAGS"] = tc.ldflags
        if self._full_version < "1.1.0" and not self.options.get_safe("no_zlib"):
            zlib_cpp_info = self.dependencies["zlib"].cpp_info.aggregated_components()
            gen_info["zlib_include_path"] = zlib_cpp_info.includedirs[0]
            if self.settings.os == "Windows":
                gen_info["zlib_lib_path"] = f"{zlib_cpp_info.libdirs[0]}/{zlib_cpp_info.libs[0]}.lib"
            else:
                gen_info["zlib_lib_path"] = zlib_cpp_info.libdirs[0]  # Just path, linux will find the right file
        save(self, "gen_info.conf", json.dumps(gen_info))
        tc = AutotoolsDeps(self)
        tc.generate()

    @property
    def _target_prefix(self):
        if self._full_version < "1.1.0" and self.settings.build_type == "Debug":
            return "debug-"
        return ""

    @property
    def _target(self):
        target = "conan-%s-%s-%s-%s-%s" % (self.settings.build_type,
                                           self.settings.os,
                                           self.settings.arch,
                                           self.settings.compiler,
                                           self.settings.compiler.version)
        if self._use_nmake:
            target = "VC-" + target  # VC- prefix is important as it's checked by Configure
        if self._is_mingw:
            target = "mingw-" + target
        return target

    @property
    def _perlasm_scheme(self):
        # right now, we need to tweak this for iOS & Android only, as they inherit from generic targets
        the_arch = str(self.settings.arch)
        the_os = str(self.settings.os)
        if the_os in ["iOS", "watchOS", "tvOS"]:
            return {"armv7": "ios32",
                    "armv7s": "ios32",
                    "armv8": "ios64",
                    "armv8_32": "ios64",
                    "armv8.3": "ios64",
                    "armv7k": "ios32"}.get(the_arch, None)
        if the_os == "Android":
            return {"armv7": "void",
                    "armv8": "linux64",
                    "mips": "o32",
                    "mips64": "64",
                    "x86": "android",
                    "x86_64": "elf"}.get(the_arch, None)
        return None

    @property
    def _asm_target(self):
        # FIXME This function is broken since https://github.com/conan-io/conan-center-index/pull/791
        # either it returns None (because the_os is not a key of the map below), or it does not return
        the_os = str(self.settings.os)
        if the_os in ["Android", "iOS", "watchOS", "tvOS"]:
            return {
                "x86": "x86_asm" if the_os == "Android" else None,
                "x86_64": "x86_64_asm" if the_os == "Android" else None,
                "armv5el": "armv4_asm",
                "armv5hf": "armv4_asm",
                "armv6": "armv4_asm",
                "armv7": "armv4_asm",
                "armv7hf": "armv4_asm",
                "armv7s": "armv4_asm",
                "armv7k": "armv4_asm",
                "armv8": "aarch64_asm",
                "armv8_32": "aarch64_asm",
                "armv8.3": "aarch64_asm",
                "mips": "mips32_asm",
                "mips64": "mips64_asm",
                "sparc": "sparcv8_asm",
                "sparcv9": "sparcv9_asm",
                "ia64": "ia64_asm",
                "ppc32be": "ppc32_asm",
                "ppc32": "ppc32_asm",
                "ppc64le": "ppc64_asm",
                "ppc64": "ppc64_asm",
                "s390": "s390x_asm",
                "s390x": "s390x_asm"
            }.get(the_os, None)

    @property
    def _targets(self):
        is_cygwin = self.settings.get_safe("os.subsystem") == "cygwin"
        is_1_0 = self._full_version < "1.1.0"
        has_darwin_arm = self._full_version >= "1.1.1i" or is_1_0
        return {
            "Linux-x86-clang": ("%slinux-generic32" % self._target_prefix) if is_1_0 else "linux-x86-clang",
            "Linux-x86_64-clang": ("%slinux-x86_64" % self._target_prefix) if is_1_0 else "linux-x86_64-clang",
            "Linux-x86-*": ("%slinux-generic32" % self._target_prefix) if is_1_0 else "linux-x86",
            "Linux-x86_64-*": "%slinux-x86_64" % self._target_prefix,
            "Linux-armv4-*": "linux-armv4",
            "Linux-armv4i-*": "linux-armv4",
            "Linux-armv5el-*": "linux-armv4",
            "Linux-armv5hf-*": "linux-armv4",
            "Linux-armv6-*": "linux-armv4",
            "Linux-armv7-*": "linux-armv4",
            "Linux-armv7hf-*": "linux-armv4",
            "Linux-armv7s-*": "linux-armv4",
            "Linux-armv7k-*": "linux-armv4",
            "Linux-armv8-*": "linux-aarch64",
            "Linux-armv8.3-*": "linux-aarch64",
            "Linux-armv8-32-*": "linux-arm64ilp32",
            "Linux-mips-*": "linux-mips32",
            "Linux-mips64-*": "linux-mips64",
            "Linux-ppc32-*": "linux-ppc32",
            "Linux-ppc32le-*": "linux-pcc32",
            "Linux-ppc32be-*": "linux-ppc32",
            "Linux-ppc64-*": "linux-ppc64",
            "Linux-ppc64le-*": "linux-ppc64le",
            "Linux-pcc64be-*": "linux-pcc64",
            "Linux-s390x-*": "linux64-s390x",
            "Linux-e2k-*": "linux-generic64",
            "Linux-sparc-*": "linux-sparcv8",
            "Linux-sparcv9-*": "linux64-sparcv9",
            "Linux-*-*": "linux-generic32",
            "Macos-x86-*": "%sdarwin-i386-cc" % self._target_prefix,
            "Macos-x86_64-*": "%sdarwin64-x86_64-cc" % self._target_prefix,
            "Macos-ppc32-*": "%sdarwin-ppc-cc" % self._target_prefix,
            "Macos-ppc32be-*": "%sdarwin-ppc-cc" % self._target_prefix,
            "Macos-ppc64-*": "darwin64-ppc-cc",
            "Macos-ppc64be-*": "darwin64-ppc-cc",
            "Macos-armv8-*": "darwin64-arm64-cc" if has_darwin_arm else "darwin-common",
            "Macos-*-*": "darwin-common",
            "iOS-x86_64-*": "darwin64-x86_64-cc",
            "iOS-*-*": "iphoneos-cross",
            "watchOS-*-*": "iphoneos-cross",
            "tvOS-*-*": "iphoneos-cross",
            # Android targets are very broken, see https://github.com/openssl/openssl/issues/7398
            "Android-armv7-*": "linux-generic32",
            "Android-armv7hf-*": "linux-generic32",
            "Android-armv8-*": "linux-generic64",
            "Android-x86-*": "linux-x86-clang",
            "Android-x86_64-*": "linux-x86_64-clang",
            "Android-mips-*": "linux-generic32",
            "Android-mips64-*": "linux-generic64",
            "Android-*-*": "linux-generic32",
            "Windows-x86-gcc": "Cygwin-x86" if is_cygwin else "mingw",
            "Windows-x86_64-gcc": "Cygwin-x86_64" if is_cygwin else "mingw64",
            "Windows-*-gcc": "Cygwin-common" if is_cygwin else "mingw-common",
            "Windows-ia64-Visual Studio": "%sVC-WIN64I" % self._target_prefix,  # Itanium
            "Windows-x86-Visual Studio": "%sVC-WIN32" % self._target_prefix,
            "Windows-x86_64-Visual Studio": "%sVC-WIN64A" % self._target_prefix,
            "Windows-armv7-Visual Studio": "VC-WIN32-ARM",
            "Windows-armv8-Visual Studio": "VC-WIN64-ARM",
            "Windows-*-Visual Studio": "VC-noCE-common",
            "Windows-ia64-clang": "%sVC-WIN64I" % self._target_prefix,  # Itanium
            "Windows-x86-clang": "%sVC-WIN32" % self._target_prefix,
            "Windows-x86_64-clang": "%sVC-WIN64A" % self._target_prefix,
            "Windows-armv7-clang": "VC-WIN32-ARM",
            "Windows-armv8-clang": "VC-WIN64-ARM",
            "Windows-*-clang": "VC-noCE-common",
            "WindowsStore-x86-*": "VC-WIN32-UWP",
            "WindowsStore-x86_64-*": "VC-WIN64A-UWP",
            "WindowsStore-armv7-*": "VC-WIN32-ARM-UWP",
            "WindowsStore-armv8-*": "VC-WIN64-ARM-UWP",
            "WindowsStore-*-*": "VC-WIN32-ONECORE",
            "WindowsCE-*-*": "VC-CE",
            "SunOS-x86-gcc": "%ssolaris-x86-gcc" % self._target_prefix,
            "SunOS-x86_64-gcc": "%ssolaris64-x86_64-gcc" % self._target_prefix,
            "SunOS-sparc-gcc": "%ssolaris-sparcv8-gcc" % self._target_prefix,
            "SunOS-sparcv9-gcc": "solaris64-sparcv9-gcc",
            "SunOS-x86-suncc": "%ssolaris-x86-cc" % self._target_prefix,
            "SunOS-x86_64-suncc": "%ssolaris64-x86_64-cc" % self._target_prefix,
            "SunOS-sparc-suncc": "%ssolaris-sparcv8-cc" % self._target_prefix,
            "SunOS-sparcv9-suncc": "solaris64-sparcv9-cc",
            "SunOS-*-*": "solaris-common",
            "*BSD-x86-*": "BSD-x86",
            "*BSD-x86_64-*": "BSD-x86_64",
            "*BSD-ia64-*": "BSD-ia64",
            "*BSD-sparc-*": "BSD-sparcv8",
            "*BSD-sparcv9-*": "BSD-sparcv9",
            "*BSD-armv8-*": "BSD-generic64",
            "*BSD-mips64-*": "BSD-generic64",
            "*BSD-ppc64-*": "BSD-generic64",
            "*BSD-ppc64le-*": "BSD-generic64",
            "*BSD-ppc64be-*": "BSD-generic64",
            "AIX-ppc32-gcc": "aix-gcc",
            "AIX-ppc64-gcc": "aix64-gcc",
            "AIX-pcc32-*": "aix-cc",
            "AIX-ppc64-*": "aix64-cc",
            "AIX-*-*": "aix-common",
            "*BSD-*-*": "BSD-generic32",
            "Emscripten-*-*": "cc",
            "Neutrino-*-*": "BASE_unix",
        }

    @property
    def _ancestor_target(self):
        if "CONAN_OPENSSL_CONFIGURATION" in os.environ:
            return os.environ["CONAN_OPENSSL_CONFIGURATION"]
        compiler = "Visual Studio" if self.settings.compiler == "msvc" else self.settings.compiler
        query = f"{self.settings.os}-{self.settings.arch}-{compiler}"
        ancestor = next((self._targets[i] for i in self._targets if fnmatch.fnmatch(query, i)), None)
        if not ancestor:
            raise ConanInvalidConfiguration(
                f"Unsupported configuration ({self.settings.os}/{self.settings.arch}/{self.settings.compiler}).\n"
                f"Please open an issue at {self.url}.\n"
                f"Alternatively, set the CONAN_OPENSSL_CONFIGURATION environment variable into your conan profile."
            )
        return ancestor

    def _tool(self, env_name, apple_name):
        if env_name in os.environ:
            return os.environ[env_name]
        if self.settings.compiler == "apple-clang":
            return getattr(XCRun(self), apple_name)
        return None

    def _patch_configure(self):
        # since _patch_makefile_org will replace binutils variables
        # use a more restricted regular expresion to prevent that Configure script trying to do it again
        configure = os.path.join(self.source_folder, "Configure")
        replace_in_file(self, configure, r"s/^AR=\s*ar/AR= $ar/;", r"s/^AR=\s*ar\b/AR= $ar/;",encoding="latin_1")

    def _adjust_path(self, path):
        return path.replace("\\", "/") if self._settings_build.os == "Windows" else path

    def _patch_makefile_org(self):
        # https://wiki.openssl.org/index.php/Compilation_and_Installation#Modifying_Build_Settings
        # its often easier to modify Configure and Makefile.org rather than trying to add targets to the configure scripts
        makefile_org = os.path.join(self.source_folder, "Makefile.org")
        if not "CROSS_COMPILE" in os.environ:
            cc = os.environ.get("CC", "cc")
            gen_info = json.loads(load(self, os.path.join(self.generators_folder, "gen_info.conf")))
            replace_in_file(self, makefile_org, "CC= cc\n", "CC= %s %s\n" % (self._adjust_path(cc), gen_info["CFLAGS"]))
            if "AR" in os.environ:
                replace_in_file(self, makefile_org, "AR=ar $(ARFLAGS) r\n", "AR=%s $(ARFLAGS) r\n" % self._adjust_path(os.environ["AR"]))
            if "RANLIB" in os.environ:
                replace_in_file(self, makefile_org, "RANLIB= ranlib\n", "RANLIB= %s\n" % self._adjust_path(os.environ["RANLIB"]))
            rc = os.environ.get("WINDRES", os.environ.get("RC"))
            if rc:
                replace_in_file(self, makefile_org, "RC= windres\n", "RC= %s\n" % self._adjust_path(rc))
            if "NM" in os.environ:
                replace_in_file(self, makefile_org, "NM= nm\n", "NM= %s\n" % self._adjust_path(os.environ["NM"]))
            if "AS" in os.environ:
                replace_in_file(self, makefile_org, "AS=$(CC) -c\n", "AS=%s\n" % self._adjust_path(os.environ["AS"]))

    def _get_default_openssl_dir(self):
        if self.settings.os == "Linux" and self._full_version >= "1.1.0":
            return "/etc/ssl"
        return "res"

    @property
    def _configure_args(self):
        openssldir = self.options.openssldir or self._get_default_openssl_dir()
        openssldir = unix_path(self, openssldir) if self.win_bash else openssldir
        args = [
          '"%s"' % (self._target if self._full_version >= "1.1.0" else self._ancestor_target),
          "shared" if self.options.shared else "no-shared",
                "--prefix=/",
                "--openssldir=\"%s\"" % openssldir,
          "no-unit-test",
          "no-threads" if self.options.no_threads else "threads"
        ]
        if self._full_version >= "1.1.1":
            args.append("PERL=%s" % self._perl)
        if self._full_version < "1.1.0" or self._full_version >= "1.1.1":
            args.append("no-tests")
        if self._full_version >= "1.1.0":
            args.append("--debug" if self.settings.build_type == "Debug" else "--release")

        args.append("--libdir=lib") # See https://github.com/openssl/openssl/blob/master/INSTALL.md#libdir

        if self.settings.os in ["tvOS", "watchOS"]:
            args.append(" -DNO_FORK") # fork is not available on tvOS and watchOS
        if self.settings.os == "Android":
            args.append(" -D__ANDROID_API__=%s" % str(self.settings.os.api_level))  # see NOTES.ANDROID
        if self.settings.os == "Emscripten":
            args.append("-D__STDC_NO_ATOMICS__=1")
        if self.settings.os == "Windows":
            if self.options.enable_capieng:
                args.append("enable-capieng")
            if self.options.capieng_dialog:
                args.append("-DOPENSSL_CAPIENG_DIALOG=1")
        else:
            args.append("-fPIC" if self.options.get_safe("fPIC", True) else "no-pic")

        args.append("no-md2" if self.options.get_safe("no_md2", True) else "enable-md2")

        if self.settings.os == "Neutrino":
            args.append("no-asm -lsocket -latomic")
        if self._is_clangcl:
            # #error <stdatomic.h> is not yet supported when compiling as C, but this is planned for a future release.
            args.append("-D__STDC_NO_ATOMICS__")
        if self._full_version < "1.1.0":
            if self.options.get_safe("no_zlib"):
                args.append("no-zlib")
            else:
                gen_info = json.loads(load(self, os.path.join(self.generators_folder, "gen_info.conf")))
                include_path = gen_info["zlib_include_path"]
                lib_path     = gen_info["zlib_lib_path"]
                # clang-cl doesn't like backslashes in #define CFLAGS (builldinf.h -> cversion.c)
                include_path = self._adjust_path(include_path)
                lib_path     = self._adjust_path(lib_path)

                if self.dependencies["zlib"].options.shared:
                    args.append("zlib-dynamic")
                else:
                    args.append("zlib")

                args.extend(['--with-zlib-include="%s"' % include_path,
                             '--with-zlib-lib="%s"' % lib_path])

        if Version(conan_version).major < 2:
            possible_values = self.options.values.fields
        else:
            possible_values = self.options.possible_values
        for option_name in possible_values:
            activated = self.options.get_safe(option_name)
            if activated and option_name not in ["fPIC", "openssldir", "capieng_dialog", "enable_capieng", "no_md2"]:
                self.output.info("activated option: %s" % option_name)
                args.append(option_name.replace("_", "-"))
        return args

    def _create_targets(self):
        config_template = """{targets} = (
    "{target}" => {{
        inherit_from => {ancestor},
        cflags => add("{cflags}"),
        cxxflags => add("{cxxflags}"),
        {defines}
        includes => add({includes}),
        lflags => add("{lflags}"),
        {shared_target}
        {shared_cflag}
        {shared_extension}
        {cc}
        {cxx}
        {ar}
        {ranlib}
        {perlasm_scheme}
    }},
);
"""
        gen_info = json.loads(load(self, os.path.join(self.generators_folder, "gen_info.conf")))
        self.output.info(f"gen_info = {gen_info}")
        cflags = []
        cxxflags = []
        cflags.extend(gen_info["CFLAGS"])
        cxxflags.extend(gen_info["CXXFLAGS"])

        cc = self._tool("CC", "cc")
        cxx = self._tool("CXX", "cxx")
        ar = self._tool("AR", "ar")
        ranlib = self._tool("RANLIB", "ranlib")

        perlasm_scheme = ""
        if self._perlasm_scheme:
            perlasm_scheme = 'perlasm_scheme => "%s",' % self._perlasm_scheme

        cc = 'cc => "%s",' % cc if cc else ""
        cxx = 'cxx => "%s",' % cxx if cxx else ""
        ar = 'ar => "%s",' % ar if ar else ""
        defines = ", ".join(f'"{d}"' for d in gen_info["DEFINES"])
        defines = 'defines => add([%s]),' % defines if defines else ""
        ranlib = 'ranlib => "%s",' % ranlib if ranlib else ""
        targets = "my %targets" if self._full_version >= "1.1.1" else "%targets"
        includes = ""

        if self._asm_target:
            ancestor = '[ "%s", asm("%s") ]' % (self._ancestor_target, self._asm_target)
        else:
            ancestor = '[ "%s" ]' % self._ancestor_target
        shared_cflag = ''
        shared_extension = ''
        shared_target = ''
        if self.settings.os == 'Neutrino':
            if self.options.shared:
                shared_extension = r'shared_extension => ".so.\$(SHLIB_VERSION_NUMBER)",'
                shared_target = 'shared_target  => "gnu-shared",'
            if self.options.get_safe("fPIC", True):
                shared_cflag='shared_cflag => "-fPIC",'

        if self.settings.os in ["iOS", "tvOS", "watchOS"] and self.conf.get("tools.apple:enable_bitcode", check_type=bool):
            cflags.append("-fembed-bitcode")
            cxxflags.append("-fembed-bitcode")
        
        config = config_template.format(targets=targets,
                                        target=self._target,
                                        ancestor=ancestor,
                                        cc=cc,
                                        cxx=cxx,
                                        ar=ar,
                                        ranlib=ranlib,
                                        cflags=" ".join(cflags),
                                        cxxflags=" ".join(cxxflags),
                                        defines=defines,
                                        includes=includes,
                                        perlasm_scheme=perlasm_scheme,
                                        shared_target=shared_target,
                                        shared_extension=shared_extension,
                                        shared_cflag=shared_cflag,
                                        lflags=" ".join(gen_info["LDFLAGS"]))
        self.output.info("using target: %s -> %s" % (self._target, self._ancestor_target))
        self.output.info(config)

        save(self, os.path.join(self.source_folder, "Configurations", "20-conan.conf"), config)

    @property
    def _perl(self):
        if self._use_nmake:
            return self.dependencies.build["strawberryperl"].conf_info.get("user.strawberryperl:perl", check_type=str)
        return "perl"

    @property
    def _nmake_makefile(self):
        return r"ms\ntdll.mak" if self.options.shared else r"ms\nt.mak"

    @contextmanager
    def _make_context(self):
        if self._use_nmake:
            # Windows: when cmake generates its cache, it populates some environment variables as well.
            # If cmake also initiates openssl build, their values (containing spaces and forward slashes)
            # break nmake (don't know about mingw make). So we fix them
            def sanitize_env_var(var):
                return '"{}"'.format(var).replace('/', '\\') if '"' not in var else var
            env = Environment()
            for key in ("CC", "RC"):
                if os.getenv(key):
                    env.define(key, sanitize_env_var(os.getenv(key)))
            with env.vars(self).apply():
                yield
        else:
            yield

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        if self._full_version >= "1.1.0":
            self._create_targets()
        else:
            self._patch_configure()
            self._patch_makefile_org()
        with self._make_context():
            with chdir(self, self.source_folder):
                # workaround for clang-cl not producing .pdb files
                if self._is_clangcl:
                    save(self, "ossl_static.pdb", "")
                args = " ".join(self._configure_args)
                self.output.info(self._configure_args)

                if self._use_nmake and self._full_version >= "1.1.0":
                    self._replace_runtime_in_file(os.path.join("Configurations", "10-main.conf"))

                self.run(f'{self._perl} ./Configure {args}')

                self._patch_install_name()

                if not self._use_nmake:
                    autotools.make()
                else:
                    if self._full_version >= "1.1.0":
                        self.run('nmake /F Makefile')
                    else: # nmake 1.0.2 support
                        # Note: 1.0.2 should not be used according to the OpenSSL Project
                        #       See https://www.openssl.org/source/

                        if not self.options.no_asm and self.settings.arch == "x86":
                            self.run(r"ms\do_nasm")
                        else:
                            self.run(r"ms\do_ms" if self.settings.arch == "x86" else r"ms\do_win64a")

                        self._replace_runtime_in_file(os.path.join("ms", "nt.mak"))
                        self._replace_runtime_in_file(os.path.join("ms", "ntdll.mak"))
                        if self.settings.arch == "x86":
                            replace_in_file(self, os.path.join("ms", "nt.mak"), "-WX", "")
                            replace_in_file(self, os.path.join("ms", "ntdll.mak"), "-WX", "")

                        # NMAKE interprets trailing backslash as line continuation
                        replace_in_file(self, self._nmake_makefile, 'INSTALLTOP=\\', 'INSTALLTOP=/')

                        self.run(f'nmake /F {self._nmake_makefile}')

    def _patch_install_name(self):
        if is_apple_os(self) and self.options.shared:
            old_str = '-install_name $(INSTALLTOP)/$(LIBDIR)/'
            new_str = '-install_name @rpath/'
            makefile = "Makefile" if self._full_version >= "1.1.1" else "Makefile.shared"
            replace_in_file(self, makefile, old_str, new_str)
        if self._use_nmake:
            # NMAKE interprets trailing backslash as line continuation
            if self._full_version >= "1.1.0":
                replace_in_file(self, "Makefile", 'INSTALLTOP_dir=\\', 'INSTALLTOP_dir=/')

    def _replace_runtime_in_file(self, filename):
        runtime = msvc_runtime_flag(self)
        for e in ["MDd", "MTd", "MD", "MT"]:
            replace_in_file(self, filename, "/{} ".format(e), "/{} ".format(runtime), strict=False)
            replace_in_file(self, filename, "/{}\"".format(e), "/{}\"".format(runtime), strict=False)

    def package(self):
        copy(self, "*LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"), keep_path=False)
        if self._use_nmake:
            args = []
            if self._full_version >= "1.1.0":
                target = "install_sw"
                args.append(f"DESTDIR={self.package_folder}")
            else: # 1.0.2 support
                target = "install"
                args.append(f"INSTALLTOP={self.package_folder}")
                openssldir = self.options.openssldir or self._get_default_openssl_dir()
                args.append(f"OPENSSLDIR={os.path.join(self.package_folder, openssldir)}")

            with chdir(self, self.source_folder):
                if self._full_version >= "1.1.0":
                    self.run(f'nmake -f Makefile {target} {" ".join(args)}')
                else: # 1.0.2 support
                    self.run(f'nmake -f {self._nmake_makefile} {target} {" ".join(args)}')
            rm(self, "*.pdb", self.package_folder, recursive=True)
            if self.settings.build_type == "Debug" and self._full_version >= "1.1.0":
                with chdir(self, os.path.join(self.package_folder, "lib")):
                    rename(self, "libssl.lib", "libssld.lib")
                    rename(self, "libcrypto.lib", "libcryptod.lib")
        else:
            autotools = Autotools(self)
            args = []
            target = "install_sw"
            if self._full_version >= "1.1.0":
                args.append(f"DESTDIR={unix_path(self, self.package_folder)}")
            else: # 1.0.2 support
                args.append(f"INSTALL_PREFIX={unix_path(self, self.package_folder)}")

            with chdir(self, self.source_folder):
                autotools.make(target=target, args=args)

            # Old OpenSSL version family has issues with permissions.
            # See https://github.com/conan-io/conan/issues/5831
            if self._full_version < "1.1.0" and self.options.shared and self.settings.os in ("Android", "FreeBSD", "Linux"):
                with chdir(self, os.path.join(self.package_folder, "lib")):
                    os.chmod("libssl.so.1.0.0", 0o755)
                    os.chmod("libcrypto.so.1.0.0", 0o755)

            if self.options.shared:
                libdir = os.path.join(self.package_folder, "lib")
                for file in os.listdir(libdir):
                    if self._is_mingw and file.endswith(".dll.a"):
                        continue
                    if file.endswith(".a"):
                        os.unlink(os.path.join(libdir, file))

            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_file_rel_path)
        )

    def _create_cmake_module_variables(self, module_file):
        content = textwrap.dedent("""\
            set(OPENSSL_FOUND TRUE)
            if(DEFINED OpenSSL_INCLUDE_DIR)
                set(OPENSSL_INCLUDE_DIR ${OpenSSL_INCLUDE_DIR})
            endif()
            if(DEFINED OpenSSL_Crypto_LIBS)
                set(OPENSSL_CRYPTO_LIBRARY ${OpenSSL_Crypto_LIBS})
                set(OPENSSL_CRYPTO_LIBRARIES ${OpenSSL_Crypto_LIBS}
                                             ${OpenSSL_Crypto_DEPENDENCIES}
                                             ${OpenSSL_Crypto_FRAMEWORKS}
                                             ${OpenSSL_Crypto_SYSTEM_LIBS})
            elseif(DEFINED openssl_OpenSSL_Crypto_LIBS_%(config)s)
                set(OPENSSL_CRYPTO_LIBRARY ${openssl_OpenSSL_Crypto_LIBS_%(config)s})
                set(OPENSSL_CRYPTO_LIBRARIES ${openssl_OpenSSL_Crypto_LIBS_%(config)s}
                                             ${openssl_OpenSSL_Crypto_DEPENDENCIES_%(config)s}
                                             ${openssl_OpenSSL_Crypto_FRAMEWORKS_%(config)s}
                                             ${openssl_OpenSSL_Crypto_SYSTEM_LIBS_%(config)s})
            endif()
            if(DEFINED OpenSSL_SSL_LIBS)
                set(OPENSSL_SSL_LIBRARY ${OpenSSL_SSL_LIBS})
                set(OPENSSL_SSL_LIBRARIES ${OpenSSL_SSL_LIBS}
                                          ${OpenSSL_SSL_DEPENDENCIES}
                                          ${OpenSSL_SSL_FRAMEWORKS}
                                          ${OpenSSL_SSL_SYSTEM_LIBS})
            elseif(DEFINED openssl_OpenSSL_SSL_LIBS_%(config)s)
                set(OPENSSL_SSL_LIBRARY ${openssl_OpenSSL_SSL_LIBS_%(config)s})
                set(OPENSSL_SSL_LIBRARIES ${openssl_OpenSSL_SSL_LIBS_%(config)s}
                                          ${openssl_OpenSSL_SSL_DEPENDENCIES_%(config)s}
                                          ${openssl_OpenSSL_SSL_FRAMEWORKS_%(config)s}
                                          ${openssl_OpenSSL_SSL_SYSTEM_LIBS_%(config)s})
            endif()
            if(DEFINED OpenSSL_LIBRARIES)
                set(OPENSSL_LIBRARIES ${OpenSSL_LIBRARIES})
            endif()
            if(DEFINED OpenSSL_VERSION)
                set(OPENSSL_VERSION ${OpenSSL_VERSION})
            endif()
        """ % {"config":str(self.settings.build_type).upper()})
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-variables.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "OpenSSL")
        self.cpp_info.set_property("cmake_build_modules", [self._module_file_rel_path])
        self.cpp_info.set_property("pkg_config_name", "openssl")

        self.cpp_info.components["crypto"].set_property("cmake_target_name", "OpenSSL::Crypto")
        self.cpp_info.components["crypto"].set_property("pkg_config_name", "libcrypto")
        self.cpp_info.components["ssl"].set_property("cmake_target_name", "OpenSSL::SSL")
        self.cpp_info.components["ssl"].set_property("pkg_config_name", "libssl")
        if self._use_nmake:
            libsuffix = "d" if self.settings.build_type == "Debug" else ""
            if self._full_version < "1.1.0":
                self.cpp_info.components["ssl"].libs = ["ssleay32"]
                self.cpp_info.components["crypto"].libs = ["libeay32"]
            else:
                self.cpp_info.components["ssl"].libs = ["libssl" + libsuffix]
                self.cpp_info.components["crypto"].libs = ["libcrypto" + libsuffix]
        else:
            self.cpp_info.components["ssl"].libs = ["ssl"]
            self.cpp_info.components["crypto"].libs = ["crypto"]

        self.cpp_info.components["ssl"].requires = ["crypto"]

        if self._full_version < "1.1.0" and not self.options.get_safe("no_zlib"):
            self.cpp_info.components["crypto"].requires = ["zlib::zlib"]

        if self.settings.os == "Windows":
            self.cpp_info.components["crypto"].system_libs.extend(["crypt32", "ws2_32", "advapi32", "user32", "bcrypt"])
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["crypto"].system_libs.extend(["dl", "rt"])
            self.cpp_info.components["ssl"].system_libs.append("dl")
            if not self.options.no_threads:
                self.cpp_info.components["crypto"].system_libs.append("pthread")
                self.cpp_info.components["ssl"].system_libs.append("pthread")
        elif self.settings.os == "Neutrino":
            self.cpp_info.components["crypto"].system_libs.append("atomic")
            self.cpp_info.components["ssl"].system_libs.append("atomic")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "OpenSSL"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenSSL"
        self.cpp_info.components["ssl"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["crypto"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["crypto"].names["cmake_find_package"] = "Crypto"
        self.cpp_info.components["crypto"].names["cmake_find_package_multi"] = "Crypto"
        self.cpp_info.components["ssl"].names["cmake_find_package"] = "SSL"
        self.cpp_info.components["ssl"].names["cmake_find_package_multi"] = "SSL"
