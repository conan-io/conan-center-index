from conans import ConanFile, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment, tools
import os

required_conan_version = ">=1.33.0"


class GetTextConan(ConanFile):
    name = "libgettext"
    description = "An internationalization and localization system for multilingual programs"
    topics = ("conan", "gettext", "intl", "libintl", "i18n")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/gettext"
    license = "GPL-3.0-or-later"
    deprecated = "gettext"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["patches/*.patch"]
    options = {"shared": [True, False], "fPIC": [True, False], "threads": ["posix", "solaris", "pth", "windows", "disabled", "auto"]}
    default_options = {"shared": False, "fPIC": True, "threads": "auto"}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    @property
    def _gettext_folder(self):
        return "gettext-tools"

    @property
    def _make_args(self):
        return ["-C", "intl"]

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

        if(self.options.threads == "auto"):
            self.options.threads = { "Solaris": "solaris", "Windows": "windows" }.get(str(self.settings.os), "posix")

    def requirements(self):
        self.requires("libiconv/1.16")

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        if self._is_msvc:
            self.build_requires("automake/1.16.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
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
                "--disable-threads" if self.options.threads == "disabled" else ("--enable-threads=" + str(self.options.threads)),
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
        self.copy(pattern="*.dll", dst="bin", src=self._source_subfolder, keep_path=False, symlinks=True)
        self.copy(pattern="*.lib", dst="lib", src=self._source_subfolder, keep_path=False, symlinks=True)
        self.copy(pattern="*.a", dst="lib", src=self._source_subfolder, keep_path=False, symlinks=True)
        self.copy(pattern="*.so*", dst="lib", src=self._source_subfolder, keep_path=False, symlinks=True)
        self.copy(pattern="*.dylib*", dst="lib", src=self._source_subfolder, keep_path=False, symlinks=True)
        self.copy(pattern="*libgnuintl.h", dst="include", src=self._source_subfolder, keep_path=False, symlinks=True)
        tools.rename(os.path.join(self.package_folder, "include", "libgnuintl.h"),
                     os.path.join(self.package_folder, "include", "libintl.h"))
        if self._is_msvc and self.options.shared:
            tools.rename(os.path.join(self.package_folder, "lib", "gnuintl.dll.lib"),
                         os.path.join(self.package_folder, "lib", "gnuintl.lib"))

    def package_info(self):
        self.cpp_info.libs = ["gnuintl"]
        if tools.is_apple_os(self.settings.os):
            self.cpp_info.frameworks.append("CoreFoundation")
