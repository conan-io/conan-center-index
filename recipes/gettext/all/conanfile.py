from conans import ConanFile, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment, tools
import os
import shutil
import glob


class GetTextConan(ConanFile):
    name = "gettext"
    description = "An internationalization and localization system for multilingual programs"
    topics = ("conan", "gettext", "intl", "libintl", "i18n")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/gettext"
    license = "GPL-3.0-or-later"
    settings = "os_build", "arch_build", "arch", "compiler", "build_type"
    exports_sources = ["patches/*.patch"]

    

    requires = ("libiconv/1.15",
                "libxml2/2.9.9")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    @property
    def _gettext_folder(self):
        return "gettext-runtime"

    @property
    def _make_args(self):
        return None

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if tools.os_info.is_windows:
            if "CONAN_BASH_PATH" not in os.environ:
                self.build_requires("msys2/20190524")
        if self._is_msvc:
            self.build_requires("automake/1.16.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "gettext-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)    
        libiconv_prefix = self.deps_cpp_info["libiconv"].rootpath
        libxml2_prefix = self.deps_cpp_info["libxml2"].rootpath
        libiconv_prefix = tools.unix_path(libiconv_prefix) if tools.os_info.is_windows else libiconv_prefix
        libxml2_prefix = tools.unix_path(libxml2_prefix) if tools.os_info.is_windows else libxml2_prefix
        args = ["HELP2MAN=/bin/true",
                "EMACS=no",
                "--disable-nls",
                "--disable-dependency-tracking",
                "--enable-relocatable",
                "--disable-c++",
                "--disable-java",
                "--disable-csharp",
                "--disable-libasprintf",
                "--disable-curses",
                "--with-libiconv-prefix=%s" % libiconv_prefix,
                "--with-libxml2-prefix=%s" % libxml2_prefix]
        build = None
        host = None
        rc = None
        if self.options.get_safe("shared"):
            args.extend(["--disable-static", "--enable-shared"])
        else:
            args.extend(["--disable-shared", "--enable-static"])
        if self._is_msvc:
            # INSTALL.windows: Native binaries, built using the MS Visual C/C++ tool chain.
            build = False
            if self.settings.arch == "x86":
                host = "i686-w64-mingw32"
                rc = "windres --target=pe-i386"
            elif self.settings.arch == "x86_64":
                host = "x86_64-w64-mingw32"
                rc = "windres --target=pe-x86-64"
            automake_perldir = os.getenv('AUTOMAKE_PERLLIBDIR')
            if automake_perldir.startswith('/mnt/'):
                automake_perldir = automake_perldir[4:]
            args.extend(["CC=%s/compile cl -nologo" % automake_perldir,
                         "LD=link",
                         "NM=dumpbin -symbols",
                         "STRIP=:",
                         "AR=%s/ar-lib lib" % automake_perldir,
                         "RANLIB=:"])
            if rc:
                args.extend(['RC=%s' % rc, 'WINDRES=%s' % rc])
        with tools.vcvars(self.settings) if self._is_msvc else tools.no_op():
            with tools.environment_append(VisualStudioBuildEnvironment(self).vars) if self._is_msvc else tools.no_op():
                with tools.chdir(os.path.join(self._source_subfolder, self._gettext_folder)):
                    env_build = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
                    if self._is_msvc:
                        env_build.flags.append("-FS")
                    env_build.configure(args=args, build=build, host=host)
                    env_build.make(self._make_args)

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        suffix = ".exe" if self.settings.os_build == "Windows" else ""
        for executable in ["gettext", "ngettext"]:
            executable += suffix
            self.copy(pattern=executable, dst="bin", src=os.path.join(self._source_subfolder, self._gettext_folder, "src"), keep_path=False)

    def package_id(self):
        self.info.include_build_settings()
        del self.info.settings.compiler
        del self.info.settings.arch

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: {}'.format(bindir))
        self.env_info.PATH.append(bindir)



