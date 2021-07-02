import os
import shutil
import stat
from conans import ConanFile, MSBuild, AutoToolsBuildEnvironment, tools


class TheoraConan(ConanFile):
    name = "theora"
    description = "Theora is a free and open video compression format from the Xiph.org Foundation"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xiph/theora"
    topics = ("conan", "theora", "video", "video-compressor", "video-format")
    license = "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    requires = (
        "ogg/1.3.4",
        "vorbis/1.3.7"
    )
    _source_subfolder = "source_subfolder"
    _autotools = None

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version][0], strip_root=True, destination=self._source_subfolder)

        source = self.conan_data["sources"][self.version][1]
        url = source["url"]
        filename = url[url.rfind("/") + 1:]
        tools.download(url, filename)
        tools.check_sha256(filename, source["sha256"])
        
        shutil.move(filename, os.path.join(self._source_subfolder, 'lib', filename))

    def _configure_autotools(self):
        if not self._autotools:
            permission = stat.S_IMODE(os.lstat("configure").st_mode)
            os.chmod("configure", (permission | stat.S_IEXEC))
            self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            configure_args = ['--disable-examples']
            if self.options.shared:
                configure_args.extend(['--disable-static', '--enable-shared'])
            else:
                configure_args.extend(['--disable-shared', '--enable-static'])
            self._autotools.configure(args=configure_args)
        return self._autotools

    def build(self):
        if self.settings.compiler == 'Visual Studio':
            self._build_msvc()
        else:
            with tools.chdir(self._source_subfolder):
                autotools = self._configure_autotools()
                autotools.make()

    def _build_msvc(self):
        # error C2491: 'rint': definition of dllimport function not allowed
        tools.replace_in_file(os.path.join(self._source_subfolder, 'examples', 'encoder_example.c'),
                              'static double rint(double x)',
                              'static double rint_(double x)')

        def format_libs(libs):
            return ' '.join([l + '.lib' for l in libs])

        # fix hard-coded library names
        project = 'libtheora'
        config = "dynamic" if self.options.shared else "static"

        vcvproj = '%s_%s.vcproj' % (project, config)
        vcvproj_path = os.path.join(self._source_subfolder, 'win32', 'VS2008', project, vcvproj)
        tools.replace_in_file(vcvproj_path,
                                'libogg.lib',
                                format_libs(self.deps_cpp_info['ogg'].libs), strict=False)
        tools.replace_in_file(vcvproj_path,
                                'libogg_static.lib',
                                format_libs(self.deps_cpp_info['ogg'].libs), strict=False)
        tools.replace_in_file(vcvproj_path,
                                'libvorbis.lib',
                                format_libs(self.deps_cpp_info['vorbis'].libs), strict=False)
        tools.replace_in_file(vcvproj_path,
                                'libvorbis_static.lib',
                                format_libs(self.deps_cpp_info['vorbis'].libs), strict=False)
        if "MT" in self.settings.compiler.runtime:
            tools.replace_in_file(vcvproj_path, 'RuntimeLibrary="2"', 'RuntimeLibrary="0"')
            tools.replace_in_file(vcvproj_path, 'RuntimeLibrary="3"', 'RuntimeLibrary="1"')

        with tools.chdir(os.path.join(self._source_subfolder, 'win32', 'VS2008', 'libtheora')):
            proj = 'libtheora_dynamic' if self.options.shared else 'libtheora_static'
            msbuild = MSBuild(self)
            try:
                # upgrade .vcproj
                msbuild.build(proj + '.vcproj', platforms={'x86': 'Win32', 'x86_64': 'x64'})
            except:
                # build .vcxproj
                msbuild.build(proj + '.vcxproj', platforms={'x86': 'Win32', 'x86_64': 'x64'})

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        if self.settings.compiler == 'Visual Studio':
            include_folder = os.path.join(self._source_subfolder, "include")
            self.copy(pattern="*.h", dst="include", src=include_folder)
            self.copy(pattern="*.dll", dst="bin", keep_path=False)
            self.copy(pattern="*.lib", dst="lib", keep_path=False)
        else:
            with tools.chdir(self._source_subfolder):
                autotools = self._configure_autotools()
                autotools.install()
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
