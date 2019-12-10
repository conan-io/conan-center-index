from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os


class LibX264Conan(ConanFile):
    name = "libx264"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.videolan.org/developers/x264.html"
    description = "x264 is a free software library and application for encoding video streams into the " \
                  "H.264/MPEG-4 AVC compression format"
    topics = ("conan", "libx264", "video", "encoding")
    license = "GPL-2.0"
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "bit_depth": [8, 10, "all"]}
    default_options = {'shared': False, 'fPIC': True, 'bit_depth': 'all'}
    build_requires = "nasm/2.13.02"
    _source_subfolder = "sources"
    _override_env = {}

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == 'gcc'

    @property
    def _is_msvc(self):
        return self.settings.compiler == 'Visual Studio'

    def build_requirements(self):
        if "CONAN_BASH_PATH" not in os.environ and tools.os_info.is_windows:
            self.build_requires("msys2/20190524")

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = 'x264-snapshot-%s-2245' % self.version
        os.rename(extracted_dir, self._source_subfolder)

    @property
    def env(self):
        ret = super(LibX264Conan, self).env
        ret.update(self._override_env)
        return ret

    def _build_configure(self):
        with tools.chdir(self._source_subfolder):
            prefix = tools.unix_path(self.package_folder)
            args = ['--disable-cli', '--prefix={}'.format(prefix)]
            if self.options.shared:
                args.append('--enable-shared')
            else:
                args.append('--enable-static')
            if self.settings.os != 'Windows' and self.options.fPIC:
                args.append('--enable-pic')
            if self.settings.build_type == 'Debug':
                args.append('--enable-debug')
            args.append('--bit-depth=%s' % str(self.options.bit_depth))

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
            env_build = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            if self._is_msvc:
                env_build.flags.append('-%s' % str(self.settings.compiler.runtime))
                # cannot open program database ... if multiple CL.EXE write to the same .PDB file, please use /FS
                env_build.flags.append('-FS')
            env_build.configure(args=args, build=False, vars=self._override_env)
            env_build.make()
            env_build.install()

    def build(self):
        if self._is_msvc:
            with tools.vcvars(self.settings):
                self._build_configure()
        else:
            self._build_configure()

    def package(self):
        self.copy(pattern="COPYING", src='sources', dst='licenses')
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

    def package_info(self):
        if self._is_msvc:
            self.cpp_info.libs = ['libx264.dll.lib' if self.options.shared else 'libx264']
            if self.options.shared:
                self.cpp_info.defines.append("X264_API_IMPORTS")
        elif self._is_mingw:
            self.cpp_info.libs = ['x264.dll' if self.options.shared else 'x264']
        else:
            self.cpp_info.libs = ['x264']
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(['dl', 'pthread', 'm'])
        if self.settings.os == "Android":
            self.cpp_info.system_libs.extend(['dl', 'm'])
        self.cpp_info.names['pkg_config'] = 'x264'
