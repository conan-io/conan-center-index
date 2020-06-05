from conans import ConanFile, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
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
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["patches/*.patch"]
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    requires = ("libiconv/1.16")

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    @property
    def _make_args(self):
        return ["-C", "intl"]

    @property
    def _gettext_folder(self):
        return "gettext-tools"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

        if self.settings.compiler == "Visual Studio" and \
           tools.Version(self.settings.compiler.version) == "15":
            raise ConanInvalidConfiguration("Gettext does not support Visual Studio 15.")

    def build_requirements(self):
        if tools.os_info.is_windows:
            if "CONAN_BASH_PATH" not in os.environ and tools.os_info.detect_windows_subsystem() != "msys2":
                self.build_requires("msys2/20190524")
        if self._is_msvc:
            self.build_requires("automake/1.16.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "gettext-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        libiconv_prefix = self.deps_cpp_info["libiconv"].rootpath
        libiconv_prefix = tools.unix_path(libiconv_prefix) if tools.os_info.is_windows else libiconv_prefix
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
                "--with-libiconv-prefix=%s" % libiconv_prefix]
        build = None
        host = None
        rc = None
        if self.options.shared:
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
            automake_perldir = tools.unix_path(os.path.join(self.deps_cpp_info['automake'].rootpath, "bin", "share", "automake-1.16"))
            args.extend(["CC=%s/compile cl -nologo" % automake_perldir,
                         "LD=link",
                         "NM=dumpbin -symbols",
                         "STRIP=:",
                         "AR=%s/ar-lib lib" % automake_perldir,
                         "RANLIB=:"])
            if rc:
                args.extend(['RC=%s' % rc, 'WINDRES=%s' % rc])
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        if self._is_msvc:
            self._autotools.flags.append("-FS")
        self._autotools.configure(args=args, build=build, host=host)
        return self._autotools

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        with tools.vcvars(self.settings) if self._is_msvc else tools.no_op():
            with tools.environment_append(VisualStudioBuildEnvironment(self).vars) if self._is_msvc else tools.no_op():
                with tools.chdir(os.path.join(self._source_subfolder)):
                    env_build = self._configure_autotools()
                    env_build.make()
                with tools.chdir(os.path.join(self._source_subfolder, self._gettext_folder)):
                    env_build.make(self._make_args)

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.dll", dst="bin", src=self._source_subfolder, keep_path=False, symlinks=True)
        self.copy(pattern="*.lib", dst="lib", src=self._source_subfolder, keep_path=False, symlinks=True)
        self.copy(pattern="*.a", dst="lib", src=self._source_subfolder, keep_path=False, symlinks=True)
        self.copy(pattern="*.so*", dst="lib", src=self._source_subfolder, keep_path=False, symlinks=True)
        self.copy(pattern="*.dylib*", dst="lib", src=self._source_subfolder, keep_path=False, symlinks=True)

        with tools.vcvars(self.settings) if self._is_msvc else tools.no_op():
            with tools.environment_append(VisualStudioBuildEnvironment(self).vars) if self._is_msvc else tools.no_op():
                with tools.chdir(os.path.join(self._source_subfolder)):
                    env_build = self._configure_autotools()
                    env_build.install()
        self.copy(pattern="*libgnuintl.h", dst="include", src=self._source_subfolder, keep_path=False, symlinks=True)
        os.rename(os.path.join(self.package_folder, "include", "libgnuintl.h"),
                  os.path.join(self.package_folder, "include", "libintl.h"))
        
        tools.rmdir(os.path.join(self.package_folder, 'share'))
        for f in glob.glob(os.path.join(self.package_folder, "lib", "*.la")):
            os.remove(f)

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: {}'.format(bindir))
        self.env_info.PATH.append(bindir)
        if self._is_msvc and self.options.shared:
            self.cpp_info.libs = ["gnuintl.dll.lib"]
        else:
            self.cpp_info.libs = ["gnuintl"]
        if self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(['CoreFoundation'])
