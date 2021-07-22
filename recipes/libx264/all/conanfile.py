from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os

required_conan_version = ">=1.33.0"


class LibX264Conan(ConanFile):
    name = "libx264"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.videolan.org/developers/x264.html"
    description = "x264 is a free software library and application for encoding video streams into the " \
                  "H.264/MPEG-4 AVC compression format"
    topics = ("conan", "libx264", "video", "encoding")
    license = "GPL-2.0"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "bit_depth": [8, 10, "all"]}
    default_options = {'shared': False, 'fPIC': True, 'bit_depth': 'all'}
    _override_env = {}
    _autotools = None

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == 'gcc'

    @property
    def _is_msvc(self):
        return self.settings.compiler == 'Visual Studio'

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        self.build_requires("nasm/2.15.05")
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def env(self):
        ret = super(LibX264Conan, self).env
        ret.update(self._override_env)
        return ret

    def _configure_autotools(self):
        if not self._autotools:
            prefix = tools.unix_path(self.package_folder)
            args = ['--disable-cli', '--prefix={}'.format(prefix)]
            if self.options.shared:
                args.append('--enable-shared')
            else:
                args.append('--enable-static')
            if self.settings.os != 'Windows' and self.options.get_safe("fPIC"):
                args.append('--enable-pic')
            if self.settings.build_type == 'Debug':
                args.append('--enable-debug')
            args.append('--bit-depth=%s' % str(self.options.bit_depth))
            if self.settings.os == "Macos" and self.settings.arch == "armv8":
                # bitstream-a.S:29:18: error: unknown token in expression
                args.append('--extra-asflags=-arch arm64')
                args.append('--extra-ldflags=-arch arm64')

            if tools.cross_building(self.settings):
                if self.settings.os == "Android":
                    # the as of ndk does not work well for building libx264
                    self._override_env["AS"] = os.environ["CC"]
                    ndk_root = tools.unix_path(os.environ["NDK_ROOT"])
                    arch = {'armv7': 'arm',
                            'armv8': 'aarch64',
                            'x86': 'i686',
                            'x86_64': 'x86_64'}.get(str(self.settings.arch))
                    abi = 'androideabi' if self.settings.arch == 'armv7' else 'android'
                    cross_prefix = "%s/bin/%s-linux-%s-" % (ndk_root, arch, abi)
                    args.append('--cross-prefix=%s' % cross_prefix)

            if self._is_msvc:
                self._override_env['CC'] = 'cl'
            self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            if self._is_msvc:
                self._autotools.flags.append('-%s' % str(self.settings.compiler.runtime))
                # cannot open program database ... if multiple CL.EXE write to the same .PDB file, please use /FS
                self._autotools.flags.append('-FS')
            build_canonical_name = None
            host_canonical_name = None
            if self.settings.compiler == "Visual Studio":
                # autotools does not know about the msvc canonical name(s)
                build_canonical_name = False
                host_canonical_name = False
            self._autotools.configure(args=args, vars=self._override_env, configure_dir=self._source_subfolder, build=build_canonical_name, host=host_canonical_name)

        return self._autotools

    def build(self):
        with tools.vcvars(self.settings) if self._is_msvc else tools.no_op():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        with tools.vcvars(self.settings) if self._is_msvc else tools.no_op():
            autotools = self._configure_autotools()
            autotools.install()
        self.copy(pattern="COPYING", src=self._source_subfolder, dst='licenses')
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))
        if self._is_msvc:
            ext = ".dll.lib" if self.options.shared else ".lib"
            tools.rename(os.path.join(self.package_folder, "lib", "libx264{}".format(ext)),
                         os.path.join(self.package_folder, "lib", "x264.lib"))

    def package_info(self):
        self.cpp_info.libs = ["x264"]
        if self._is_msvc and self.options.shared:
            self.cpp_info.defines.append("X264_API_IMPORTS")
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(['dl', 'pthread', 'm'])
        elif self.settings.os == "Android":
            self.cpp_info.system_libs.extend(['dl', 'm'])
        self.cpp_info.names['pkg_config'] = 'x264'
