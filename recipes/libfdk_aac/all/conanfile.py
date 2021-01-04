from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os
import fnmatch


class FDKAACConan(ConanFile):
    name = "libfdk_aac"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A standalone library of the Fraunhofer FDK AAC code from Android"
    license = "https://github.com/mstorsjo/fdk-aac/blob/master/NOTICE"
    settings = "os", "arch", "compiler", "build_type"
    homepage = "https://sourceforge.net/projects/opencore-amr/"
    topics = ("conan", "libfdk_aac", "multimedia", "audio", "fraunhofer", "aac", "decoder", "encoding", "decoding")
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, 'fPIC': True}
    _source_subfolder = 'sources'

    @property
    def _use_winbash(self):
        return tools.os_info.is_windows and (self.settings.compiler == 'gcc' or tools.cross_building(self.settings))

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def build_requirements(self):
        if self._use_winbash and self.settings.compiler != 'Visual Studio':
            if "CONAN_BASH_PATH" not in os.environ and tools.os_info.detect_windows_subsystem() != 'msys2':
                self.build_requires("msys2/20190524")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "fdk-aac-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _build_vs(self):
        with tools.chdir(self._source_subfolder):
            with tools.vcvars(self.settings, force=True):
                with tools.remove_from_path('mkdir'):
                    tools.replace_in_file('Makefile.vc',
                                          'CFLAGS   = /nologo /W3 /Ox /MT',
                                          'CFLAGS   = /nologo /W3 /Ox /%s' % str(self.settings.compiler.runtime))
                    tools.replace_in_file('Makefile.vc',
                                          'MKDIR_FLAGS = -p',
                                          'MKDIR_FLAGS =')
                    self.run('nmake -f Makefile.vc')
                    self.run('nmake -f Makefile.vc prefix="%s" install' % os.path.abspath(self.package_folder))

    def _build_configure(self):
        with tools.chdir(self._source_subfolder):
            win_bash = self._use_winbash
            prefix = os.path.abspath(self.package_folder)
            if self._use_winbash:
                prefix = tools.unix_path(prefix, tools.MSYS2)
            args = ['--prefix=%s' % prefix]
            if self.options.shared:
                args.extend(['--disable-static', '--enable-shared'])
            else:
                args.extend(['--disable-shared', '--enable-static'])
            env_build = AutoToolsBuildEnvironment(self, win_bash=win_bash)
            self.run('autoreconf -fiv', win_bash=win_bash)
            if self.settings.os == "Android" and tools.os_info.is_windows:
                # remove escape for quotation marks, to make ndk on windows happy
                tools.replace_in_file('configure',
                    "s/[	 `~#$^&*(){}\\\\|;'\\\''\"<>?]/\\\\&/g", "s/[	 `~#$^&*(){}\\\\|;<>?]/\\\\&/g")
            env_build.configure(args=args)
            env_build.make()
            env_build.install()

    def build(self):
        if self.settings.compiler == 'Visual Studio':
            self._build_vs()
        else:
            self._build_configure()

    def package(self):
        self.copy(pattern="NOTICE", src='sources', dst="licenses")
        if self.settings.compiler == 'Visual Studio':
            if self.options.shared:
                exts = ['fdk-aac.lib']
            else:
                exts = ['fdk-aac.dll.lib', 'fdk-aac-1.dll']
            for root, _, filenames in os.walk(self.package_folder):
                for ext in exts:
                    for filename in fnmatch.filter(filenames, ext):
                        os.unlink(os.path.join(root, filename))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))
        if os.path.isfile(os.path.join(self.package_folder, "lib", "libfdk-aac.la")):
            os.remove(os.path.join(self.package_folder, "lib", "libfdk-aac.la"))

    def package_info(self):
        if self.settings.compiler == 'Visual Studio' and self.options.shared:
            self.cpp_info.libs = ['fdk-aac.dll.lib']
        else:
            self.cpp_info.libs = ['fdk-aac']
        if self.settings.os == "Linux" or self.settings.os == "Android":
            self.cpp_info.system_libs.append("m")
        self.cpp_info.names['pkg_config'] = 'fdk-aac'
