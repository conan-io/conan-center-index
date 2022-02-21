from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil

required_conan_version = ">=1.33.0"


class LibVPXConan(ConanFile):
    name = "libvpx"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.webmproject.org/code"
    description = "WebM VP8/VP9 Codec SDK"
    topics = ("vpx", "codec", "web", "VP8", "VP9")
    license = "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _arch_options = ['mmx', 'sse', 'sse2', 'sse3', 'ssse3', 'sse4_1', 'avx', 'avx2', 'avx512']

    options.update({name: [True, False] for name in _arch_options})
    default_options.update({name: 'avx' not in name for name in _arch_options})

    exports_sources = "patches/*"
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
        if str(self.settings.arch) not in ['x86', 'x86_64']:
            for name in self._arch_options:
                delattr(self.options, name)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Windows shared builds are not supported")
        if self.settings.compiler not in ["Visual Studio", "gcc", "clang", "apple-clang"]:
            raise ConanInvalidConfiguration("Unsupported compiler {}.".format(self.settings.compiler))
        if self.settings.os == "Macos" and self.settings.arch == "armv8" and tools.Version(self.version) < "1.10.0":
            raise ConanInvalidConfiguration("M1 only supported since 1.10, please upgrade")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        self.build_requires("yasm/1.3.0")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        win_bash = tools.os_info.is_windows
        prefix = os.path.abspath(self.package_folder)
        if win_bash:
            prefix = tools.unix_path(prefix)
        args = ['--prefix=%s' % prefix,
                '--disable-examples',
                '--disable-unit-tests',
                '--disable-tools',
                '--disable-docs',
                '--enable-vp9-highbitdepth',
                '--as=yasm']
        if self.options.shared:
            args.extend(['--disable-static', '--enable-shared'])
        else:
            args.extend(['--disable-shared', '--enable-static'])
        if self.settings.os != 'Windows' and self.options.get_safe("fPIC", True):
            args.append('--enable-pic')
        if self.settings.build_type == "Debug":
            args.append('--enable-debug')
        if self.settings.compiler == 'Visual Studio':
            if 'MT' in str(self.settings.compiler.runtime):
                args.append('--enable-static-msvcrt')

        arch = {'x86': 'x86',
                'x86_64': 'x86_64',
                'armv7': 'armv7',
                'armv8': 'arm64',
                'mips': 'mips32',
                'mips64': 'mips64',
                'sparc': 'sparc'}.get(str(self.settings.arch))
        host_compiler = str(self.settings.compiler)
        if host_compiler == 'Visual Studio':
            compiler = 'vs' + str(self.settings.compiler.version)
        elif host_compiler in ['gcc', 'clang', 'apple-clang']:
            compiler = 'gcc'

        host_os = str(self.settings.os)
        if host_os == 'Windows':
            os_name = 'win32' if self.settings.arch == 'x86' else 'win64'
        elif tools.is_apple_os(host_os):
            if self.settings.arch in ["x86", "x86_64"]:
                os_name = 'darwin11'
            elif self.settings.arch == "armv8" and self.settings.os == "Macos":
                os_name = 'darwin20'
            else:
                # Unrecognized toolchain 'arm64-darwin11-gcc', see list of toolchains in ./configure --help
                os_name = 'darwin'
        elif host_os == 'Linux':
            os_name = 'linux'
        elif host_os == 'Solaris':
            os_name = 'solaris'
        elif host_os == 'Android':
            os_name = 'android'
        target = "%s-%s-%s" % (arch, os_name, compiler)
        args.append('--target=%s' % target)
        if str(self.settings.arch) in ["x86", "x86_64"]:
            for name in self._arch_options:
                if not self.options.get_safe(name):
                    args.append('--disable-%s' % name)
        with tools.vcvars(self.settings) if self.settings.compiler == 'Visual Studio' else tools.no_op():
            self._autotools = AutoToolsBuildEnvironment(self, win_bash=win_bash)
            if self.settings.compiler == "Visual Studio":
                # gen_msvs_vcxproj.sh doesn't like custom flags
                self._autotools.cxxflags = []
                self._autotools.flags = []
            if tools.is_apple_os(self.settings.os) and self.settings.get_safe("compiler.libcxx") == "libc++":
                # special case, as gcc/g++ is hard-coded in makefile, it implicitly assumes -lstdc++
                self._autotools.link_flags.append("-stdlib=libc++")
            self._autotools.configure(args=args, configure_dir=self._source_subfolder, host=False, build=False, target=False)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        with tools.vcvars(self.settings) if self.settings.compiler == "Visual Studio" else tools.no_op():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        with tools.vcvars(self.settings) if self.settings.compiler == "Visual Studio" else tools.no_op():
            autotools = self._configure_autotools()
            autotools.install()

        self.copy(pattern="LICENSE", src=self._source_subfolder, dst='licenses')
        if self.settings.os == 'Windows' and self.settings.compiler == 'Visual Studio':
            name = 'vpxmt.lib' if 'MT' in str(self.settings.compiler.runtime) else 'vpxmd.lib'
            if self.settings.arch == 'x86_64':
                libdir = os.path.join(self.package_folder, 'lib', 'x64')
            elif self.settings.arch == 'x86':
                libdir = os.path.join(self.package_folder, 'lib', 'Win32')
            shutil.move(os.path.join(libdir, name), os.path.join(self.package_folder, 'lib', 'vpx.lib'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "vpx"
        self.cpp_info.libs = ["vpx"]
