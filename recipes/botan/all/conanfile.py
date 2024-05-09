import os
import shutil
import platform

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name, XCRun
from conan.tools.build import build_jobs, check_min_cppstd
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get
from conan.tools.gnu import AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, msvc_runtime_flag, VCVars, check_min_vs
from conan.tools.microsoft import unix_path
from conan.tools.scm import Version


required_conan_version = ">=1.55"


class BotanConan(ConanFile):
    name = "botan"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/randombit/botan"
    license = "BSD-2-Clause"
    description = "Botan is a cryptography library written in modern C++."
    topics = ("cryptography", "crypto", "c++11", "c++20", "tls")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "amalgamation": [True, False],
        "with_bzip2": [True, False],
        "with_openssl": [True, False],
        "with_sqlite3": [True, False],
        "with_zlib": [True, False],
        "with_boost": [True, False],
        "with_sse2": [True, False],
        "with_ssse3": [True, False],
        "with_sse4_1": [True, False],
        "with_sse4_2": [True, False],
        "with_avx2": [True, False],
        "with_bmi2": [True, False],
        "with_rdrand": [True, False],
        "with_rdseed": [True, False],
        "with_aes_ni": [True, False],
        "with_sha_ni": [True, False],
        "with_altivec": [True, False],
        "with_neon": [True, False],
        "with_armv8crypto": [True, False],
        "with_powercrypto": [True, False],
        "enable_modules": [None, "ANY"],
        "disable_modules": [None, "ANY"],
        "system_cert_bundle": [None, "ANY"],
        "module_policy": [None, "bsi", "modern", "nist"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "amalgamation": True,
        "with_bzip2": False,
        "with_openssl": False,
        "with_sqlite3": False,
        "with_zlib": False,
        "with_boost": False,
        "with_sse2": True,
        "with_ssse3": True,
        "with_sse4_1": True,
        "with_sse4_2": True,
        "with_avx2": True,
        "with_bmi2": True,
        "with_rdrand": True,
        "with_rdseed": True,
        "with_aes_ni": True,
        "with_sha_ni": True,
        "with_altivec": True,
        "with_neon": True,
        "with_armv8crypto": True,
        "with_powercrypto": True,
        "enable_modules": None,
        "disable_modules": None,
        "system_cert_bundle": None,
        "module_policy": None,
    }

    _extra_cxxflags = None

    @property
    def _is_x86(self):
        return str(self.settings.arch) in ['x86', 'x86_64']

    @property
    def _is_ppc(self):
        return 'ppc' in str(self.settings.arch)

    @property
    def _is_arm(self):
        return 'arm' in str(self.settings.arch)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == 'Windows':
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

        # Support for the OpenSSL provider was removed in 2.19.2
        if Version(self.version) >= '2.19.2':
            del self.options.with_openssl

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        if self.options.with_bzip2:
            self.requires("bzip2/1.0.8")
        if self.options.get_safe('with_openssl', False):
            self.requires("openssl/[>=1.1 <3]")
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_sqlite3:
            self.requires("sqlite3/3.45.1")
        if self.options.with_boost:
            self.requires("boost/1.84.0")

    @property
    def _required_boost_components(self):
        return ['coroutine', 'system']

    @property
    def _min_cppstd(self):
        # From the same links as below
        return 11 if Version(self.version) < "3.0.0" else 20

    @property
    def _compilers_minimum_version(self):
        if Version(self.version).major < 3:
            # From https://github.com/randombit/botan/blob/2.19.3/doc/support.rst
            return {
                "gcc": "4.8",
                "clang": "3.5",
                "Visual Studio": "14",
                "msvc": "190",
            }
        else:
            # From https://github.com/randombit/botan/blob/master/doc/support.rst
            return {
                "gcc":  "11.2",
                "clang": "14",
                "apple-clang": "14",
                "Visual Studio": "17",
                "msvc": "193",
            }

    def validate(self):
        if self.options.with_boost:
            boost_opts = self.dependencies['boost'].options
            miss_boost_required_comp = any(getattr(boost_opts, 'without_{}'.format(boost_comp), True) for boost_comp in self._required_boost_components)
            if boost_opts.header_only or boost_opts.shared or boost_opts.magic_autolink or miss_boost_required_comp:
                raise ConanInvalidConfiguration(
                    f"{self.name} requires non-header-only static boost, "
                    f"without magic_autolink, and with these components: {', '.join(self._required_boost_components)}")
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        compiler = self.settings.compiler
        compiler_name = str(compiler)
        compiler_version = Version(compiler.version)

        check_min_vs(self, self._compilers_minimum_version["msvc"])
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(compiler_name, False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support (minimum {compiler_name} {minimum_version})."
                )
            if not minimum_version:
                self.output.warning(f"{self.name} recipe lacks information about the {compiler_name} compiler support.")

        if self.settings.compiler == 'gcc' and compiler_version >= "5" and self.settings.compiler.libcxx != 'libstdc++11':
            raise ConanInvalidConfiguration(
                'Using Botan with GCC >= 5 on Linux requires "compiler.libcxx=libstdc++11"')

        if self.settings.compiler == 'clang' and self.settings.compiler.libcxx not in ['libstdc++11', 'libc++']:
            raise ConanInvalidConfiguration(
                'Using Botan with Clang on Linux requires either "compiler.libcxx=libstdc++11" ' \
                'or "compiler.libcxx=libc++"')

        # Some older compilers cannot handle the amalgamated build anymore
        # See also https://github.com/randombit/botan/issues/2328
        if self.options.amalgamation:
            if (self.settings.compiler == 'apple-clang' and compiler_version < '10') or \
               (self.settings.compiler == 'gcc' and compiler_version < '8') or \
               (self.settings.compiler == 'clang' and compiler_version < '7'):
                raise ConanInvalidConfiguration(
                    f"botan amalgamation is not supported for {compiler}/{compiler_version}")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _cxxflags(self):
        global_cxxflags = " ".join(self.conf.get("tools.build:cxxflags", default=[], check_type=list))
        env_cxxflags = VirtualBuildEnv(self).vars().get("CXXFLAGS", default="")
        cxxflags = f"{env_cxxflags} {global_cxxflags}".strip()
        return cxxflags if len(cxxflags) > 1 else None

    def generate(self):
        if is_msvc(self):
            ms = VCVars(self)
            ms.generate()

        # This is to work around botan's configure script that *replaces* its
        # standard (platform dependent) flags in presence of an environment
        # variable ${CXXFLAGS}. Most notably, this would build botan with
        # disabled compiler optimizations.
        self._extra_cxxflags = self._cxxflags
        self.buildenv.unset('CXXFLAGS')
        VirtualBuildEnv(self).generate()

    def build(self):
        apply_conandata_patches(self)
        with chdir(self, self.source_folder):
            self.run(self._configure_cmd)
            self.run(self._make_cmd)

    def package(self):
        copy(self, "license.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        with chdir(self, self.source_folder):
            # Note: this will fail to properly consider the package_folder if a "conan build" followed by a "conan export-pkg" is executed
            self.run(self._make_install_cmd)
        fix_apple_shared_install_name(self)

    def package_info(self):
        major_version = Version(self.version).major
        self.cpp_info.set_property("pkg_config_name", f"botan-{major_version}")
        self.cpp_info.libs = ["botan" if is_msvc(self) and major_version < 3 else f"botan-{major_version}"]
        if self.settings.os == 'Linux':
            self.cpp_info.system_libs.extend(['dl', 'rt', 'pthread', 'm'])
        if self.settings.os == 'Macos':
            self.cpp_info.frameworks = ['Security', 'CoreFoundation']
        if self.settings.os == 'Windows':
            self.cpp_info.system_libs.extend(['ws2_32', 'crypt32'])

        self.cpp_info.includedirs = [os.path.join("include", f"botan-{major_version}")]

    @property
    def _is_mingw_windows(self):
        return self.settings.os == 'Windows' and self.settings.compiler == 'gcc'

    @property
    def _botan_os(self):
        if self._is_mingw_windows:
            return 'mingw'
        return {'Windows': 'windows',
                'Linux': 'linux',
                'Macos': 'darwin',
                'Android': 'linux',
                'baremetal': 'none',
                'iOS': 'ios'}.get(str(self.settings.os))

    def _dependency_build_flags(self, dependency):
        # Since botan has a custom build system, we need to specifically inject
        # these build parameters so that it picks up the correct dependencies.
        dep_cpp_info = self.dependencies[dependency].cpp_info
        return \
            ['--with-external-includedir={}'.format(include_path) for include_path in dep_cpp_info.includedirs] + \
            ['--with-external-libdir={}'.format(lib_path) for lib_path in dep_cpp_info.libdirs] + \
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
            botan_abi_flags.extend(['-stdlib=libc++', '-lc++abi'])

        if self.settings.compiler in ['clang', 'apple-clang', 'gcc']:
            if self.settings.arch == 'x86':
                botan_abi_flags.append('-m32')
            elif self.settings.arch == 'x86_64':
                botan_abi_flags.append('-m64')

        if self.settings.compiler in ['apple-clang']:
            if self.settings.arch in ['armv7']:
                botan_abi_flags.append('-arch armv7')
            elif self.settings.arch in ['armv8']:
                botan_abi_flags.append('-arch arm64')
            elif self.settings.arch in ['x86_64']:
                botan_abi_flags.append('-arch x86_64')

        if self.options.get_safe('fPIC', True) and not is_msvc(self):
            botan_extra_cxx_flags.append('-fPIC')

        if is_apple_os(self):
            if self.settings.get_safe('os.version'):
                # Required, see https://github.com/conan-io/conan-center-index/pull/3456
                macos_min_version = macos_min_version = AutotoolsToolchain(self).apple_min_version_flag
                botan_extra_cxx_flags.append(macos_min_version)
            macos_sdk_path = '-isysroot {}'.format(XCRun(self).sdk_path)
            botan_extra_cxx_flags.append(macos_sdk_path)

        if self._extra_cxxflags:
            botan_extra_cxx_flags.append(self._extra_cxxflags)

        if self.options.enable_modules:
            build_flags.append('--minimized-build')
            build_flags.append('--enable-modules={}'.format(self.options.enable_modules))

        if self.options.disable_modules:
            build_flags.append('--disable-modules={}'.format(self.options.disable_modules))

        if self.options.amalgamation:
            build_flags.append('--amalgamation')

        if self.options.system_cert_bundle:
            build_flags.append('--system-cert-bundle={}'.format(self.options.system_cert_bundle))

        if self.conf.get("tools.build:sysroot"):
            build_flags.append(f'--with-sysroot-dir={self.conf.get("tools.build:sysroot")}')

        if self.options.with_bzip2:
            build_flags.append('--with-bzip2')
            build_flags.extend(self._dependency_build_flags('bzip2'))

        if self.options.get_safe('with_openssl', False):
            build_flags.append('--with-openssl')
            build_flags.extend(self._dependency_build_flags('openssl'))

        if self.options.with_sqlite3:
            build_flags.append('--with-sqlite3')
            build_flags.extend(self._dependency_build_flags('sqlite3'))

        if self.options.with_zlib:
            build_flags.append('--with-zlib')
            build_flags.extend(self._dependency_build_flags('zlib'))

        if self.options.with_boost:
            build_flags.append('--with-boost')
            build_flags.extend(self._dependency_build_flags('boost'))

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

        build_targets = ['shared'] if self.options.shared else ['static']

        if self._is_mingw_windows:
            build_flags.append('--without-stack-protector')

        if is_msvc(self):
            build_flags.append(f"--msvc-runtime={msvc_runtime_flag(self)}")

        if self._is_glibc_older_than_2_25_on_linux and Version(self.version) >= '3.0':
            # INFO: Botan 3.0+ requires glibc >= 2.25. Disable features to make it backward compatible
            # FIXME: CCI Docker images are running Ubuntu 16.04. Remove it after supporting later version.
            self.output.warning("Disabling usage of getentropy(), getrandom(), and explicit_bzero() due to old glibc version")
            build_flags.append('--without-os-features=getentropy,getrandom,explicit_bzero')

        build_flags.append('--without-pkg-config')

        call_python = 'python' if self.settings.os == 'Windows' else ''

        prefix = unix_path(self, self.package_folder) if self._is_mingw_windows else self.package_folder

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
                             targets=','.join(build_targets),
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
        return self._nmake_cmd if is_msvc(self) else self._gnumake_cmd

    @property
    def _make_program(self):
        return self.conf.get("tools.gnu:make_program", os.getenv('CONAN_MAKE_PROGRAM', shutil.which('make') or shutil.which('mingw32-make')))

    @property
    def _gnumake_cmd(self):
        make_ldflags = 'LDFLAGS=-lc++abi' if self._is_linux_clang_libcxx else ''

        make_cmd = f"{make_ldflags} {self._make_program} -j{build_jobs(self)}"
        return make_cmd

    @property
    def _nmake_cmd(self):
        return 'nmake'

    @property
    def _make_install_cmd(self):
        if is_msvc(self):
            make_install_cmd = '{make} install'.format(make=self._nmake_cmd)
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

    @property
    def _is_glibc_older_than_2_25_on_linux(self):
        # FIXME: glibc below 2.25 lacks support for certain syscalls that botan assumes
        # to be present. Once CCI updated their CI images and provides a newer
        # glibc, we can (and should) remove this workaround.
        #
        # https://github.com/conan-io/conan-center-index/pull/18079#issuecomment-1919206949
        # https://github.com/conan-io/conan-center-index/pull/18079#issuecomment-1919486839

        libver = platform.libc_ver()
        return (
            self.settings.os == 'Linux' and
            libver[0] == 'glibc' and
            Version(libver[1]) < '2.25'
        )
