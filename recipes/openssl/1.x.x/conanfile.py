from conan import ConanFile, conan_version
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os, XCRun
from conan.tools.build import cross_building
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import (
    apply_conandata_patches, chdir, copy, export_conandata_patches,
    get, load, replace_in_file, rm, rmdir, save
)
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, msvc_runtime_flag, unix_path
from conan.tools.scm import Version
from contextlib import contextmanager
import fnmatch
import json
import os
import textwrap

required_conan_version = ">=1.53.0"


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
        "no_md5": [True, False],
        "no_mdc2": [True, False],
        "no_rc2": [True, False],
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
        "openssldir": [None, "ANY"],
    }
    default_options = {key: False for key in options.keys()}
    default_options["fPIC"] = True
    default_options["openssldir"] = None

    @property
    def _is_clang_cl(self):
        return self.settings.os == "Windows" and self.settings.compiler == "clang" and \
               self.settings.compiler.get_safe("runtime")

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    @property
    def _use_nmake(self):
        return self._is_clang_cl or is_msvc(self)

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        else:
            del self.options.capieng_dialog
            del self.options.enable_capieng

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

    def validate(self):
        if self.settings.os == "Emscripten":
            if not all((self.options.no_asm, self.options.no_threads, self.options.no_stdio, self.options.no_tests)):
                raise ConanInvalidConfiguration("os=Emscripten requires openssl:{no_asm,no_threads,no_stdio,no_tests}=True")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            if not self.options.no_asm:
                self.tool_requires("nasm/2.16.01")
            if self._use_nmake:
                self.tool_requires("strawberryperl/5.32.1.1")
            else:
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                    self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()

        tc = AutotoolsToolchain(self)
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
        save(self, "gen_info.conf", json.dumps(gen_info))
        tc = AutotoolsDeps(self)
        tc.generate()

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
    def _targets(self):
        is_cygwin = self.settings.get_safe("os.subsystem") == "cygwin"
        return {
            "Linux-x86-clang": "linux-x86-clang",
            "Linux-x86_64-clang": "linux-x86_64-clang",
            "Linux-x86-*": "linux-x86",
            "Linux-x86_64-*": "linux-x86_64",
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
            "Macos-x86-*": "darwin-i386-cc",
            "Macos-x86_64-*": "darwin64-x86_64-cc",
            "Macos-ppc32-*": "darwin-ppc-cc",
            "Macos-ppc32be-*": "darwin-ppc-cc",
            "Macos-ppc64-*": "darwin64-ppc-cc",
            "Macos-ppc64be-*": "darwin64-ppc-cc",
            "Macos-armv8-*": "darwin64-arm64-cc",
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
            "Windows-ia64-Visual Studio": "VC-WIN64I",  # Itanium
            "Windows-x86-Visual Studio": "VC-WIN32",
            "Windows-x86_64-Visual Studio": "VC-WIN64A",
            "Windows-armv7-Visual Studio": "VC-WIN32-ARM",
            "Windows-armv8-Visual Studio": "VC-WIN64-ARM",
            "Windows-*-Visual Studio": "VC-noCE-common",
            "Windows-ia64-clang": "VC-WIN64I",  # Itanium
            "Windows-x86-clang": "VC-WIN32",
            "Windows-x86_64-clang": "VC-WIN64A",
            "Windows-armv7-clang": "VC-WIN32-ARM",
            "Windows-armv8-clang": "VC-WIN64-ARM",
            "Windows-*-clang": "VC-noCE-common",
            "WindowsStore-x86-*": "VC-WIN32-UWP",
            "WindowsStore-x86_64-*": "VC-WIN64A-UWP",
            "WindowsStore-armv7-*": "VC-WIN32-ARM-UWP",
            "WindowsStore-armv8-*": "VC-WIN64-ARM-UWP",
            "WindowsStore-*-*": "VC-WIN32-ONECORE",
            "WindowsCE-*-*": "VC-CE",
            "SunOS-x86-gcc": "solaris-x86-gcc",
            "SunOS-x86_64-gcc": "solaris64-x86_64-gcc",
            "SunOS-sparc-gcc": "solaris-sparcv8-gcc",
            "SunOS-sparcv9-gcc": "solaris64-sparcv9-gcc",
            "SunOS-x86-suncc": "solaris-x86-cc",
            "SunOS-x86_64-suncc": "solaris64-x86_64-cc",
            "SunOS-sparc-suncc": "solaris-sparcv8-cc",
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

    def _get_default_openssl_dir(self):
        if self.settings.os == "Linux":
            return "/etc/ssl"
        return "res"

    @property
    def _configure_args(self):
        openssldir = self.options.openssldir or self._get_default_openssl_dir()
        openssldir = unix_path(self, openssldir) if self.win_bash else openssldir
        args = [
            f'"{self._target}"',
            "shared" if self.options.shared else "no-shared",
            "--prefix=/",
            f"--openssldir=\"{openssldir}\"",
            "no-unit-test",
            "no-threads" if self.options.no_threads else "threads",
            f"PERL={self._perl}",
            "no-tests",
            "--debug" if self.settings.build_type == "Debug" else "--release",
            "--libdir=lib", # See https://github.com/openssl/openssl/blob/master/INSTALL.md#libdir
        ]

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

        args.append("no-md2")

        if self.settings.os == "Neutrino":
            args.append("no-asm -lsocket -latomic")
        if self._is_clang_cl:
            # #error <stdatomic.h> is not yet supported when compiling as C, but this is planned for a future release.
            args.append("-D__STDC_NO_ATOMICS__")

        if Version(conan_version).major < 2:
            possible_values = self.options.values.fields
        else:
            possible_values = self.options.possible_values
        for option_name in possible_values:
            activated = self.options.get_safe(option_name)
            if activated and option_name not in ["fPIC", "openssldir", "capieng_dialog", "enable_capieng"]:
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
        targets = "my %targets"
        includes = ""

        ancestor = f'[ "{self._ancestor_target}" ]'
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
        self._create_targets()
        with self._make_context():
            with chdir(self, self.source_folder):
                # workaround for clang-cl not producing .pdb files
                if self._is_clang_cl:
                    save(self, "ossl_static.pdb", "")
                args = " ".join(self._configure_args)
                self.output.info(self._configure_args)

                if self._use_nmake:
                    self._replace_runtime_in_file(os.path.join("Configurations", "10-main.conf"))

                self.run(f'{self._perl} ./Configure {args}')

                self._patch_install_name()

                if self._use_nmake:
                    self.run("nmake /F Makefile")
                else:
                    autotools.make()

    def _patch_install_name(self):
        if is_apple_os(self) and self.options.shared:
            old_str = '-install_name $(INSTALLTOP)/$(LIBDIR)/'
            new_str = '-install_name @rpath/'
            replace_in_file(self, "Makefile", old_str, new_str)
        if self._use_nmake:
            # NMAKE interprets trailing backslash as line continuation
            replace_in_file(self, "Makefile", 'INSTALLTOP_dir=\\', 'INSTALLTOP_dir=/')

    def _replace_runtime_in_file(self, filename):
        runtime = msvc_runtime_flag(self)
        for e in ["MDd", "MTd", "MD", "MT"]:
            replace_in_file(self, filename, "/{} ".format(e), "/{} ".format(runtime), strict=False)
            replace_in_file(self, filename, "/{}\"".format(e), "/{}\"".format(runtime), strict=False)

    def package(self):
        copy(self, "*LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"), keep_path=False)
        if self._use_nmake:
            with chdir(self, self.source_folder):
                self.run(f"nmake -f Makefile install_sw DESTDIR={self.package_folder}")
            rm(self, "*.pdb", self.package_folder, recursive=True)
        else:
            autotools = Autotools(self)
            with chdir(self, self.source_folder):
                args = [f"DESTDIR={unix_path(self, self.package_folder)}"]
                autotools.make(target="install_sw", args=args)

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
            self.cpp_info.components["ssl"].libs = ["libssl"]
            self.cpp_info.components["crypto"].libs = ["libcrypto"]
        else:
            self.cpp_info.components["ssl"].libs = ["ssl"]
            self.cpp_info.components["crypto"].libs = ["crypto"]

        self.cpp_info.components["ssl"].requires = ["crypto"]

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
            self.cpp_info.components["crypto"].system_libs.append("socket")
            self.cpp_info.components["ssl"].system_libs.append("socket")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "OpenSSL"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenSSL"
        self.cpp_info.components["ssl"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["crypto"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["crypto"].names["cmake_find_package"] = "Crypto"
        self.cpp_info.components["crypto"].names["cmake_find_package_multi"] = "Crypto"
        self.cpp_info.components["ssl"].names["cmake_find_package"] = "SSL"
        self.cpp_info.components["ssl"].names["cmake_find_package_multi"] = "SSL"
