import os
from conans import ConanFile, tools
from conans.errors import ConanException, ConanInvalidConfiguration
from conans.tools import Version


class BotanConan(ConanFile):
    name = 'botan'
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/randombit/botan"
    license = "BSD-2-Clause"
    exports = ["patches/*"]
    description = "Botan is a cryptography library written in C++11."
    topics = ("cryptography", "crypto", "C++11", "tls")
    settings = 'os', 'arch', 'compiler', 'build_type'
    options = {
        'amalgamation': [True, False],
        'with_bzip2': [True, False],
        'with_openssl': [True, False],
        'shared': [True, False],
        'fPIC': [True, False],
        'single_amalgamation': [True, False],
        'with_sqlite3': [True, False],
        'with_zlib': [True, False],
        'with_boost': [True, False],
        'with_sse2': [True, False],
        'with_ssse3': [True, False],
        'with_sse4_1': [True, False],
        'with_sse4_2': [True, False],
        'with_avx2': [True, False],
        'with_bmi2': [True, False],
        'with_rdrand': [True, False],
        'with_rdseed': [True, False],
        'with_aes_ni': [True, False],
        'with_sha_ni': [True, False],
        'with_altivec': [True, False],
        'with_neon': [True, False],
        'with_armv8crypto': [True, False],
        'with_powercrypto': [True, False],
        'enable_modules': "ANY",
        'system_cert_bundle': "ANY",
        'module_policy': [None, 'bsi', 'modern', 'nist']
    }
    default_options = {'amalgamation': True,
                       'with_bzip2': False,
                       'with_openssl': False,
                       'shared': False,
                       'fPIC': True,
                       'single_amalgamation': False,
                       'with_sqlite3': False,
                       'with_zlib': False,
                       'with_boost': False,
                       'with_sse2': True,
                       'with_ssse3': True,
                       'with_sse4_1': True,
                       'with_sse4_2': True,
                       'with_avx2': True,
                       'with_bmi2': True,
                       'with_rdrand': True,
                       'with_rdseed': True,
                       'with_aes_ni': True,
                       'with_sha_ni': True,
                       'with_altivec': True,
                       'with_neon': True,
                       'with_armv8crypto': True,
                       'with_powercrypto': True,
                       'enable_modules': None,
                       'system_cert_bundle': None,
                       'module_policy': None}

    @property
    def _is_x86(self):
        return str(self.settings.arch) in ["x86", "x86_64"]

    @property
    def _is_ppc(self):
        return "ppc" in str(self.settings.arch)

    @property
    def _is_arm(self):
        return "arm" in str(self.settings.arch)

    def configure(self):
        self._validate_compiler_settings()

        if Version(self.version) >= "2.14.0":
            self._validate_v2_14()

        if self.options.get_safe("single_amalgamation"):
            self.options.amalgamation = True

        if self.options.with_boost:
            self.options["boost"].add("shared=False")
            self.options["boost"].add("magic_autolink=False")
            self.options["boost"].add("without_coroutine=False")
            self.options["boost"].add("without_system=False")

    def requirements(self):
        if self.options.with_bzip2:
            self.requires("bzip2/1.0.6")
        if self.options.with_openssl:
            self.requires("openssl/1.1.1i")
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.with_sqlite3:
            self.requires("sqlite3/3.30.1")
        if self.options.with_boost:
            self.requires("boost/1.71.0")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._is_x86:
            del self.options.with_sse2
            del self.options.with_ssse3
            del self.options.with_sse4_1
            del self.options.with_sse4_2
            del self.options.with_avx2
            del self.options.with_bmi2
            del self.options.with_rdrand
            del self.options.with_rdseed
            del self.options.with_aes_ni
            del self.options.with_sha_ni
        if not self._is_arm:
            del self.options.with_neon
            del self.options.with_armv8crypto
        if not self._is_ppc:
            del self.options.with_altivec
            del self.options.with_powercrypto

        # --single-amalgamation option is no longer available
        # See also https://github.com/randombit/botan/pull/2246
        if Version(self.version) >= "2.14.0":
            del self.options.single_amalgamation

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "botan-" + self.version
        os.rename(extracted_dir, "sources")

    def build(self):
        if "patches" in self.conan_data:
            if self.version in self.conan_data["patches"]:
                for patch in self.conan_data["patches"][self.version]:
                    tools.patch(**patch)
        with tools.chdir('sources'):
            self.run(self._configure_cmd)
            self.run(self._make_cmd)

    def package(self):
        self.copy(pattern="license.txt", dst="licenses", src="sources")
        with tools.chdir("sources"):
            self.run(self._make_install_cmd)

    def package_info(self):
        if self.settings.compiler == 'Visual Studio':
            self.cpp_info.libs.append('botan')
        else:
            self.cpp_info.libs.extend(['botan-2'])
            if self.settings.os != 'Windows':
                self.cpp_info.system_libs.append('dl')
            if self.settings.os == 'Linux':
                self.cpp_info.system_libs.append('rt')
            if self.settings.os == 'Macos':
                self.cpp_info.frameworks = ['Security', 'CoreFoundation']
            if not self.options.shared:
                self.cpp_info.system_libs.append('pthread')
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "Crypt32"])

        self.cpp_info.includedirs = ['include/botan-2']

    def _validate_compiler_settings(self):
        compiler = self.settings.compiler
        version = Version(self.settings.compiler.version.value)

        if compiler == "Visual Studio" and version < "14":
            raise ConanInvalidConfiguration("Botan doesn't support MSVC < 14")

        elif compiler == "gcc" and version >= "5" and compiler.libcxx != "libstdc++11":
            raise ConanInvalidConfiguration(
                'Using Botan with GCC >= 5 on Linux requires "compiler.libcxx=libstdc++11"')

        elif compiler == "clang" and compiler.libcxx not in ["libstdc++11", "libc++"]:
            raise ConanInvalidConfiguration(
                'Using Botan with Clang on Linux requires either "compiler.libcxx=libstdc++11" ' \
                'or "compiler.libcxx=libc++"')

    def _validate_v2_14(self):
        """disallow configurations that cause issues in Botan >= 2.14.0"""

        compiler = self.settings.compiler
        compiler_version = Version(compiler.version.value)

        # Some older compilers cannot handle the amalgamated build anymore
        # See also https://github.com/randombit/botan/issues/2328
        if self.options.amalgamation:
            if (compiler == "apple-clang" and compiler_version < "10") or \
               (compiler == "gcc" and compiler_version < "8") or \
               (compiler == "clang" and compiler_version < "7"):
                raise ConanInvalidConfiguration(
                    "amalgamation is not supported for {} {}".format(compiler, compiler_version))

    @property
    def _is_mingw_windows(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    @property
    def _botan_os(self):
        if self._is_mingw_windows:
            return "mingw"
        return {"Windows": "windows",
                "Linux": "linux",
                "Macos": "darwin",
                "Android": "linux",
                "iOS": "ios"}.get(str(self.settings.os))

    def _dependency_build_flags(self, dependency):
        # Since botan has a custom build system, we need to specifically inject
        # these build parameters so that it picks up the correct dependencies.
        dep_cpp_info = self.deps_cpp_info[dependency]
        return \
            ['--with-external-includedir={}'.format(include_path) for include_path in dep_cpp_info.include_paths] + \
            ['--with-external-libdir={}'.format(lib_path) for lib_path in dep_cpp_info.lib_paths] + \
            ['--define-build-macro={}'.format(define) for define in dep_cpp_info.defines]

    @property
    def _configure_cmd(self):
        if self.settings.compiler in ('clang', 'apple-clang'):
            botan_compiler = 'clang'
        elif self.settings.compiler == 'gcc':
            botan_compiler = 'gcc'
        else:
            botan_compiler = 'msvc'

        botan_abi_flags = []
        botan_extra_cxx_flags = []
        build_flags = []

        if self._is_linux_clang_libcxx:
            botan_abi_flags.extend(["-stdlib=libc++", "-lc++abi"])

        if botan_compiler in ['clang', 'apple-clang', 'gcc']:
            if self.settings.arch == "x86":
                botan_abi_flags.append('-m32')
            elif self.settings.arch == "x86_64":
                botan_abi_flags.append('-m64')

        if self.settings.os != "Windows" and self.options.fPIC:
            botan_extra_cxx_flags.append('-fPIC')

        if tools.is_apple_os(self.settings.os):
            if self.settings.get_safe("os.version"):
                macos_min_version = tools.apple_deployment_target_flag(self.settings.os,
                                                                       self.settings.get_safe("os.version"),
                                                                       self.settings.get_safe("os.sdk"),
                                                                       self.settings.get_safe("os.subsystem"),
                                                                       self.settings.get_safe("arch"))
                botan_extra_cxx_flags.append(macos_min_version)
            macos_sdk_path = "-isysroot {}".format(tools.XCRun(self.settings).sdk_path)
            botan_extra_cxx_flags.append(macos_sdk_path)

        # This is to work around botan's configure script that *replaces* its
        # standard (platform dependent) flags in presence of an environment
        # variable ${CXXFLAGS}. Most notably, this would build botan with
        # disabled compiler optimizations.
        environment_cxxflags = tools.get_env("CXXFLAGS")
        if environment_cxxflags:
            del os.environ["CXXFLAGS"]
            botan_extra_cxx_flags.append(environment_cxxflags)

        if self.options.enable_modules:
            build_flags.append('--minimized-build')
            build_flags.append('--enable-modules={}'.format(self.options.enable_modules))

        if self.options.amalgamation:
            build_flags.append('--amalgamation')

        if self.options.get_safe("single_amalgamation"):
            build_flags.append('--single-amalgamation-file')

        if self.options.system_cert_bundle:
            build_flags.append('--system-cert-bundle={}'.format(self.options.system_cert_bundle))

        if self.options.with_bzip2:
            build_flags.append('--with-bzip2')
            build_flags.extend(self._dependency_build_flags("bzip2"))

        if self.options.with_openssl:
            build_flags.append('--with-openssl')
            build_flags.extend(self._dependency_build_flags("openssl"))

        if self.options.with_sqlite3:
            build_flags.append('--with-sqlite3')
            build_flags.extend(self._dependency_build_flags("sqlite3"))

        if self.options.with_zlib:
            build_flags.append('--with-zlib')
            build_flags.extend(self._dependency_build_flags("zlib"))

        if self.options.with_boost:
            build_flags.append('--with-boost')
            build_flags.extend(self._dependency_build_flags("boost"))

        if self.options.module_policy:
            build_flags.append('--module-policy={}'.format(self.options.module_policy))

        if self.settings.build_type == 'RelWithDebInfo':
            build_flags.append('--with-debug-info')

        if self._is_x86:
            if not self.options.with_sse2:
                build_flags.append('--disable-sse2')

            if not self.options.with_ssse3:
                build_flags.append('--disable-ssse3')

            if not self.options.with_sse4_1:
                build_flags.append('--disable-sse4.1')

            if not self.options.with_sse4_2:
                build_flags.append('--disable-sse4.2')

            if not self.options.with_avx2:
                build_flags.append('--disable-avx2')

            if not self.options.with_bmi2:
                build_flags.append('--disable-bmi2')

            if not self.options.with_rdrand:
                build_flags.append('--disable-rdrand')

            if not self.options.with_rdseed:
                build_flags.append('--disable-rdseed')

            if not self.options.with_aes_ni:
                build_flags.append('--disable-aes-ni')

            if not self.options.with_sha_ni:
                build_flags.append('--disable-sha-ni')

        if self._is_ppc:
            if not self.options.with_powercrypto:
                build_flags.append('--disable-powercrypto')

            if not self.options.with_altivec:
                build_flags.append('--disable-altivec')

        if self._is_arm:
            if not self.options.with_neon:
                build_flags.append('--disable-neon')

            if not self.options.with_armv8crypto:
                build_flags.append('--disable-armv8crypto')

        if str(self.settings.build_type).lower() == 'debug':
            build_flags.append('--debug-mode')

        build_targets = ["shared"] if self.options.shared else ["static"]

        if self._is_mingw_windows:
            build_flags.append('--without-stack-protector')

        if self.settings.compiler == 'Visual Studio':
            build_flags.append('--msvc-runtime=%s' % str(self.settings.compiler.runtime))

        build_flags.append('--without-pkg-config')

        call_python = 'python' if self.settings.os == 'Windows' else ''

        prefix = tools.unix_path(self.package_folder) if self._is_mingw_windows else self.package_folder

        botan_abi = ' '.join(botan_abi_flags) if botan_abi_flags else ' '
        botan_cxx_extras = ' '.join(botan_extra_cxx_flags) if botan_extra_cxx_flags else ' '

        configure_cmd = ('{python_call} ./configure.py'
                         ' --build-targets={targets}'
                         ' --distribution-info="Conan"'
                         ' --without-documentation'
                         ' --cc-abi-flags="{abi}"'
                         ' --extra-cxxflags="{cxxflags}"'
                         ' --cc={compiler}'
                         ' --cpu={cpu}'
                         ' --prefix={prefix}'
                         ' --os={os}'
                         ' {build_flags}').format(
                             python_call=call_python,
                             targets=",".join(build_targets),
                             abi=botan_abi,
                             cxxflags=botan_cxx_extras,
                             compiler=botan_compiler,
                             cpu=self.settings.arch,
                             prefix=prefix,
                             os=self._botan_os,
                             build_flags=' '.join(build_flags))

        return configure_cmd

    @property
    def _make_cmd(self):
        return self._nmake_cmd if self.settings.compiler == 'Visual Studio' else self._gnumake_cmd

    @property
    def _make_program(self):
        return tools.get_env("CONAN_MAKE_PROGRAM", tools.which("make") or tools.which('mingw32-make'))

    @property
    def _gnumake_cmd(self):
        make_ldflags = 'LDFLAGS=-lc++abi' if self._is_linux_clang_libcxx else ''

        make_cmd = ('{ldflags}'
                    ' {make}'
                    ' -j{cpucount}').format(
                        ldflags=make_ldflags,
                        make=self._make_program,
                        cpucount=tools.cpu_count())
        return make_cmd

    @property
    def _nmake_cmd(self):
        vcvars = tools.vcvars_command(self.settings)
        make_cmd = vcvars + ' && nmake'
        return make_cmd

    @property
    def _make_install_cmd(self):
        if self.settings.compiler == 'Visual Studio':
            vcvars = tools.vcvars_command(self.settings)
            make_install_cmd = vcvars + ' && nmake install'
        else:
            make_install_cmd = '{make} install'.format(make=self._make_program)
        return make_install_cmd

    @property
    def _is_linux_clang_libcxx(self):
        return (
            self.settings.os == 'Linux' and
            self.settings.compiler == 'clang' and
            self.settings.compiler.libcxx == 'libc++'
        )
