import os

from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
from conans.tools import Version


class LcmsConan(ConanFile):
    name = "lcms"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A free, open source, CMM engine."
    license = "MIT"
    homepage = "https://github.com/mm2/Little-CMS"
    author = "Bicrafters <bincrafters@gmail.com>"
    topics = ("conan", "lcms", "cmm", "icc", "cmm-engine")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, 'fPIC': True}
    generators = "cmake"
    _source_subfolder = "source_subfolder"

    def build_requirements(self):
        if tools.os_info.is_windows and "CONAN_BASH_PATH" not in os.environ:
            self.build_requires("msys2/20161025")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename('Little-CMS-lcms%s' % self.version, self._source_subfolder)

    def _build_visual_studio(self):
        # since VS2015 vsnprintf is built-in
        if Version(self.settings.compiler.version) >= "14":
            path = os.path.join(self._source_subfolder, 'src', 'lcms2_internal.h')
            tools.replace_in_file(path, '#       define vsnprintf  _vsnprintf', '')

        with tools.chdir(os.path.join(self._source_subfolder, 'Projects', 'VC2013')):
            target = 'lcms2_DLL' if self.options.shared else 'lcms2_static'
            upgrade_project = Version(self.settings.compiler.version) > "12"
            # run build
            msbuild = MSBuild(self)
            msbuild.build("lcms2.sln", targets=[target], platforms={"x86": "Win32"}, upgrade_project=upgrade_project)

    def _build_configure(self):
        if self.settings.os == "Android" and tools.os_info.is_windows:
            # remove escape for quotation marks, to make ndk on windows happy
            tools.replace_in_file(os.path.join(self._source_subfolder, 'configure'),
                "s/[	 `~#$^&*(){}\\\\|;'\\\''\"<>?]/\\\\&/g", "s/[	 `~#$^&*(){}\\\\|;<>?]/\\\\&/g")
        env_build = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        with tools.chdir(self._source_subfolder):
            args = ['prefix=%s' % self.package_folder]
            if self.options.shared:
                args.extend(['--disable-static', '--enable-shared'])
            else:
                args.extend(['--disable-shared', '--enable-static'])
            args.append('--without-tiff')
            args.append('--without-jpeg')
            env_build.configure(args=args)
            env_build.make()
            env_build.make(args=['install'])

    def build(self):
        if self.settings.compiler == 'Visual Studio':
            self._build_visual_studio()
        else:
            self._build_configure()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        if self.settings.compiler == 'Visual Studio':
            self.copy(pattern='*.h', src=os.path.join(self._source_subfolder, 'include'), dst='include', keep_path=True)
            if self.options.shared:
                self.copy(pattern='*.lib', src=os.path.join(self._source_subfolder, 'bin'), dst='lib', keep_path=False)
                self.copy(pattern='*.dll', src=os.path.join(self._source_subfolder, 'bin'), dst='bin', keep_path=False)
            else:
                self.copy(pattern='*.lib', src=os.path.join(self._source_subfolder, 'Lib', 'MS'), dst='lib',
                          keep_path=False)
        # remove entire share directory
        tools.rmdir(os.path.join(self.package_folder, 'share'))
        # remove pkgconfig
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))
        # remove la files
        la = os.path.join(self.package_folder, 'lib', 'liblcms2.la')
        if os.path.isfile(la):
            os.unlink(la)
        # remove binaries
        for bin_program in ['tificc', 'linkicc', 'transicc', 'psicc', 'jpgicc']:
            for ext in ['', '.exe']:
                try:
                    os.remove(os.path.join(self.package_folder, 'bin', bin_program + ext))
                except:
                    pass

    def package_info(self):
        if self.settings.compiler == 'Visual Studio':
            self.cpp_info.libs = ['lcms2' if self.options.shared else 'lcms2_static']
            if self.options.shared:
                self.cpp_info.defines.append('CMS_DLL')
        else:
            self.cpp_info.libs = ['lcms2']
