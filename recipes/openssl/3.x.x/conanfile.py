import os
import fnmatch
import platform
from conans.errors import ConanInvalidConfiguration, ConanException
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.tools import Version


class OpenSSLConan(ConanFile):
    name = "openssl"
    settings = "os", "compiler", "arch", "build_type"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/openssl/openssl"
    license = "Apache-2.0"
    topics = ("conan", "openssl", "ssl", "tls", "encryption", "security")
    description = "A toolkit for the Transport Layer Security (TLS) and Secure Sockets Layer (SSL) protocols"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "386": [True, False],
        "capieng_dialog": [True, False],
        "enable_capieng": [True, False],
        "no_asm": [True, False],
        "no_async": [True, False],
        "no_bf": [True, False],
        "no_cast": [True, False],
        "no_deprected": [True, False],
        "no_des": [True, False],
        "no_dh": [True, False],
        "no_dsa": [True, False],
        "no_dso": [True, False],
        "no_engine": [True, False],
        "no_fips": [True, False],
        "no_hmac": [True, False],
        "no_legacy": [True, False],
        "no_md5": [True, False],
        "no_mdc2": [True, False],
        "no_rc2": [True, False],
        "no_rc4": [True, False],
        "no_rsa": [True, False],
        "no_sha": [True, False],
        "no_sse2": [True, False],
        "no_threads": [True, False],
        "openssldir": "ANY",
        "zlib": [True, False]
        }
    default_options = {key: False for key in options.keys()}
    default_options["fPIC"] = True
    default_options["zlib"] = True
    default_options["openssldir"] = None
    _env_build = None
    _source_subfolder = "source_subfolder"
    exports_sources = ["patches/*"]

    def build_requirements(self):
        if tools.os_info.is_windows:
            if not self._win_bash:
                self.build_requires("strawberryperl/5.30.0.1")
            if not self.options.no_asm and not tools.which("nasm"):
                self.build_requires("nasm/2.14")
        if self._win_bash:
            if "CONAN_BASH_PATH" not in os.environ:
                self.build_requires("msys2/20200517")

    def requirements(self):
        if self.options.get_safe("zlib") == True:
            self.requires("zlib/1.2.11")

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    @property
    def _is_clangcl(self):
        return self.settings.compiler == "clang" and self.settings.os == "Windows"

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    @property
    def _use_nmake(self):
        return self._is_clangcl or self._is_msvc

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def config_options(self):
        if self.settings.os != "Windows":
            del self.options.capieng_dialog
            del self.options.enable_capieng
        else:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "openssl-" + self.version
        os.rename(extracted_folder, self._source_subfolder)

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
        elif the_os == "Android":
            return {"armv7": "void",
                    "armv8": "linux64",
                    "mips": "o32",
                    "mips64": "64",
                    "x86": "android",
                    "x86_64": "elf"}.get(the_arch, None)
        return None

    @property
    def _asm_target(self):
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
        query = "%s-%s-%s" % (self.settings.os, self.settings.arch, self.settings.compiler)
        ancestor = next((self._targets[i] for i in self._targets if fnmatch.fnmatch(query, i)), None)
        if not ancestor:
            raise ConanInvalidConfiguration("Unsupported configuration: %s %s %s, "
                                            "please open an issue: "
                                            "https://github.com/conan-io/conan-center-index/issues. "
                                            "alternatively, set the CONAN_OPENSSL_CONFIGURATION environment variable "
                                            "into your conan profile "
                                            "(list of configurations can be found by running './Configure --help')." %
                                            (self.settings.os,
                                            self.settings.arch,
                                            self.settings.compiler))
        return ancestor

    def _tool(self, env_name, apple_name):
        if env_name in os.environ:
            return os.environ[env_name]
        if self.settings.compiler == "apple-clang":
            return getattr(tools.XCRun(self.settings), apple_name)
        return None

    def _patch_configure(self):
        # since _patch_makefile_org will replace binutils variables
        # use a more restricted regular expresion to prevent that Configure script trying to do it again
        configure = os.path.join(self._source_subfolder, "Configure")
        tools.replace_in_file(configure, r"s/^AR=\s*ar/AR= $ar/;", r"s/^AR=\s*ar\b/AR= $ar/;")

    def _patch_makefile_org(self):
        # https://wiki.openssl.org/index.php/Compilation_and_Installation#Modifying_Build_Settings
        # its often easier to modify Configure and Makefile.org rather than trying to add targets to the configure scripts
        def adjust_path(path):
            return path.replace("\\", "/") if tools.os_info.is_windows else path

        makefile_org = os.path.join(self._source_subfolder, "Makefile.org")
        env_build = self._get_env_build()
        with tools.environment_append(env_build.vars):
            if not "CROSS_COMPILE" in os.environ:
                cc = os.environ.get("CC", "cc")
                tools.replace_in_file(makefile_org, "CC= cc\n", "CC= %s %s\n" % (adjust_path(cc), os.environ["CFLAGS"]))
                if "AR" in os.environ:
                    tools.replace_in_file(makefile_org, "AR=ar $(ARFLAGS) r\n", "AR=%s $(ARFLAGS) r\n" % adjust_path(os.environ["AR"]))
                if "RANLIB" in os.environ:
                    tools.replace_in_file(makefile_org, "RANLIB= ranlib\n", "RANLIB= %s\n" % adjust_path(os.environ["RANLIB"]))
                rc = os.environ.get("WINDRES", os.environ.get("RC"))
                if rc:
                    tools.replace_in_file(makefile_org, "RC= windres\n", "RC= %s\n" % adjust_path(rc))
                if "NM" in os.environ:
                    tools.replace_in_file(makefile_org, "NM= nm\n", "NM= %s\n" % adjust_path(os.environ["NM"]))
                if "AS" in os.environ:
                    tools.replace_in_file(makefile_org, "AS=$(CC) -c\n", "AS=%s\n" % adjust_path(os.environ["AS"]))

    def _get_env_build(self):
        if not self._env_build:
            self._env_build = AutoToolsBuildEnvironment(self)
            if self.settings.compiler == "apple-clang":
                # add flags only if not already specified, avoid breaking Catalyst which needs very special flags
                flags = " ".join(self._env_build.flags)
                if "-arch" not in flags:
                    self._env_build.flags.append("-arch %s" % tools.to_apple_arch(self.settings.arch))
                if "-isysroot" not in flags:
                    self._env_build.flags.append("-isysroot %s" % tools.XCRun(self.settings).sdk_path)
                if self.settings.get_safe("os.version") and "-version-min=" not in flags and "-target" not in flags:
                    self._env_build.flags.append(tools.apple_deployment_target_flag(self.settings.os,
                                                                              self.settings.os.version))
        return self._env_build

    @property
    def _configure_args(self):
        openssldir = self.options.openssldir if self.options.openssldir else os.path.join(self.package_folder, "res")
        prefix = tools.unix_path(self.package_folder) if self._win_bash else self.package_folder
        openssldir = tools.unix_path(openssldir) if self._win_bash else openssldir
        args = [
            '"%s"' % (self._target),
            "shared" if self.options.shared else "no-shared",
                "--prefix=\"%s\"" % prefix,
                "--openssldir=\"%s\"" % openssldir,
            "no-unit-test",
            "no-threads" if self.options.no_threads else "threads"
        ]
        args.append("PERL=%s" % self._perl)
        args.append("no-tests")
        args.append("--debug" if self.settings.build_type == "Debug" else "--release")

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
            args.append("-fPIC" if self.options.fPIC else "no-pic")
        if self.settings.os == "Neutrino":
            args.append("-lsocket no-asm")

        if self.options.get_safe("zlib") == True:
            zlib_info = self.deps_cpp_info["zlib"]
            include_path = zlib_info.include_paths[0]
            if self.settings.os == "Windows":
                lib_path = "%s/%s.lib" % (zlib_info.lib_paths[0], zlib_info.libs[0])
            else:
                # Just path, linux will find the right file
                lib_path = zlib_info.lib_paths[0]
            if tools.os_info.is_windows:
                # clang-cl doesn't like backslashes in #define CFLAGS (builldinf.h -> cversion.c)
                include_path = include_path.replace('\\', '/')
                lib_path = lib_path.replace('\\', '/')

            if zlib_info.shared:
                args.append("zlib-dynamic")
            else:
                args.append("zlib")

            args.extend([
                '--with-zlib-include="%s"' % include_path,
                '--with-zlib-lib="%s"' % lib_path
            ])

        for option_name in self.options.values.fields:
            activated = getattr(self.options, option_name)
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
        cflags = []

        env_build = self._get_env_build()
        cflags.extend(env_build.flags)
        cxxflags = cflags[:]
        cxxflags.extend(env_build.cxx_flags)

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
        defines = " ".join(env_build.defines)
        defines = 'defines => add("%s"),' % defines if defines else ""
        ranlib = 'ranlib => "%s",' % ranlib if ranlib else ""
        targets = "my %targets"
        includes = ", ".join(['"%s"' % include for include in env_build.include_paths])
        if self.settings.os == "Windows":
            includes = includes.replace('\\', '/') # OpenSSL doesn't like backslashes

        if self._asm_target:
            ancestor = '[ "%s", asm("%s") ]' % (self._ancestor_target, self._asm_target)
        else:
            ancestor = '[ "%s" ]' % self._ancestor_target
        shared_cflag = ''
        shared_extension = ''
        shared_target = ''
        if self.settings.os == 'Neutrino':
            if self.options.shared:
                shared_extension = 'shared_extension => ".so.\$(SHLIB_VERSION_NUMBER)",'
                shared_target = 'shared_target  => "gnu-shared",'
            if self.options.fPIC:
                shared_cflag = 'shared_cflag => "-fPIC",'

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
                                        lflags=" ".join(env_build.link_flags))
        self.output.info("using target: %s -> %s" % (self._target, self._ancestor_target))
        self.output.info(config)

        tools.save(os.path.join(self._source_subfolder, "Configurations", "20-conan.conf"), config)

    def _run_make(self, targets=None, makefile=None, parallel=True):
        command = [self._make_program]
        if makefile:
            command.extend(["-f", makefile])
        if targets:
            command.extend(targets)
        if not self._use_nmake:
            command.append(("-j%s" % tools.cpu_count()) if parallel else "-j1")
        self.run(" ".join(command), win_bash=self._win_bash)

    @property
    def _perl(self):
        if tools.os_info.is_windows and not self._win_bash:
            # enforce strawberry perl, otherwise wrong perl could be used (from Git bash, MSYS, etc.)
            return os.path.join(self.deps_cpp_info["strawberryperl"].rootpath, "bin", "perl.exe")
        return "perl"

    @property
    def _nmake_makefile(self):
        return r"ms\ntdll.mak" if self.options.shared else r"ms\nt.mak"

    def _make(self):
        with tools.chdir(self._source_subfolder):
            # workaround for clang-cl not producing .pdb files
            if self._is_clangcl:
                tools.save("ossl_static.pdb", "")
            args = " ".join(self._configure_args)
            self.output.info(self._configure_args)

            if self._use_nmake:
                self._replace_runtime_in_file(os.path.join("Configurations", "10-main.conf"))

            self.run('{perl} ./Configure {args}'.format(perl=self._perl, args=args), win_bash=self._win_bash)

            self._patch_install_name()

            self._run_make()

    def _make_install(self):
        with tools.chdir(self._source_subfolder):
            self._run_make(targets=["install_sw"], parallel=False)

    @property
    def _cc(self):
        if "CROSS_COMPILE" in os.environ:
            return "gcc"
        if "CC" in os.environ:
            return os.environ["CC"]
        if self.settings.compiler == "apple-clang":
            return tools.XCRun(self.settings).find("clang")
        elif self.settings.compiler == "clang":
            return "clang"
        elif self.settings.compiler == "gcc":
            return "gcc"
        return "cc"

    def build(self):
        with tools.vcvars(self.settings) if self._use_nmake else tools.no_op():
            env_vars = {"PERL": self._perl}
            if self.settings.compiler == "apple-clang":
                xcrun = tools.XCRun(self.settings)
                env_vars["CROSS_SDK"] = os.path.basename(xcrun.sdk_path)
                env_vars["CROSS_TOP"] = os.path.dirname(os.path.dirname(xcrun.sdk_path))
            with tools.environment_append(env_vars):
                self._create_targets()
                self._make()

    @property
    def _win_bash(self):
        return tools.os_info.is_windows and \
               not self._use_nmake and \
            (self._is_mingw or tools.cross_building(self.settings, skip_x64_x86=True))

    @property
    def _make_program(self):
        if self._use_nmake:
            return "nmake"
        make_program = tools.get_env("CONAN_MAKE_PROGRAM", tools.which("make") or tools.which("mingw32-make"))
        make_program = tools.unix_path(make_program) if tools.os_info.is_windows else make_program
        if not make_program:
            raise Exception('could not find "make" executable. please set "CONAN_MAKE_PROGRAM" environment variable')
        return make_program

    def _patch_install_name(self):
        if self.settings.os == "Macos" and self.options.shared:
            old_str = '-install_name $(INSTALLTOP)/$(LIBDIR)/'
            new_str = '-install_name '

            tools.replace_in_file("Makefile", old_str, new_str, strict=self.in_local_cache)

    def _replace_runtime_in_file(self, filename):
        for e in ["MDd", "MTd", "MD", "MT"]:
            tools.replace_in_file(filename, "/%s " % e, "/%s " % self.settings.compiler.runtime, strict=False)
            tools.replace_in_file(filename, "/%s\"" % e, "/%s\"" % self.settings.compiler.runtime, strict=False)

    def package(self):
        self.copy(pattern="*LICENSE*", dst="licenses", src=self._source_subfolder)
        with tools.vcvars(self.settings) if self._use_nmake else tools.no_op():
            self._make_install()
        for root, _, files in os.walk(self.package_folder):
            for filename in files:
                if fnmatch.fnmatch(filename, "*.pdb"):
                    os.unlink(os.path.join(self.package_folder, root, filename))
        if self._use_nmake:
            if self.settings.build_type == "Debug":
                with tools.chdir(os.path.join(self.package_folder, "lib")):
                    os.rename("libssl.lib", "libssld.lib")
                    os.rename("libcrypto.lib", "libcryptod.lib")

        if self.options.shared:
            libdir = os.path.join(self.package_folder, "lib")
            for file in os.listdir(libdir):
                if self._is_mingw and file.endswith(".dll.a"):
                    continue
                if file.endswith(".a"):
                    os.unlink(os.path.join(libdir, file))

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "OpenSSL"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenSSL"
        if self._use_nmake:
            libsuffix = "d" if self.settings.build_type == "Debug" else ""
            self.cpp_info.components["ssl"].libs = ["libssl" + libsuffix]
            self.cpp_info.components["crypto"].libs = ["libcrypto" + libsuffix]
        else:
            self.cpp_info.components["ssl"].libs = ["ssl"]
            self.cpp_info.components["crypto"].libs = ["crypto"]

        self.cpp_info.components["ssl"].requires = ["crypto"]

        if self.options.get_safe("zlib"):
            self.cpp_info.components["crypto"].requires = ["zlib::zlib"]

        if self.settings.os == "Windows":
            self.cpp_info.components["crypto"].system_libs.extend(["crypt32", "ws2_32", "advapi32", "user32"])
        elif self.settings.os == "Linux":
            self.cpp_info.components["crypto"].system_libs.append("dl")
            self.cpp_info.components["ssl"].system_libs.append("dl")
            if not self.options.no_threads:
                self.cpp_info.components["crypto"].system_libs.append("pthread")
                self.cpp_info.components["ssl"].system_libs.append("pthread")

        self.cpp_info.components["crypto"].names["cmake_find_package"] = "Crypto"
        self.cpp_info.components["crypto"].names["cmake_find_package_multi"] = "Crypto"
        self.cpp_info.components["crypto"].names["pkg_config"] = "libcrypto"
        self.cpp_info.components["ssl"].names["cmake_find_package"] = "SSL"
        self.cpp_info.components["ssl"].names["cmake_find_package_multi"] = "SSL"
        self.cpp_info.components["ssl"].names["pkg_config"] = "libssl"
