from conans import ConanFile, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment, tools
import os

required_conan_version = ">=1.43.0"


class GetTextConan(ConanFile):
    name = "libgettext"
    description = "An internationalization and localization system for multilingual programs"
    topics = ("gettext", "intl", "libintl", "i18n")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/gettext"
    license = "GPL-3.0-or-later"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "threads": ["posix", "solaris", "pth", "windows", "disabled", "auto"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "threads": "auto",
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _is_clang_cl(self):
        return str(self.settings.compiler) in ["clang"] and str(self.settings.os) in ["Windows"]

    @property
    def _gettext_folder(self):
        return "gettext-tools"

    @property
    def _make_args(self):
        return ["-C", "intl"]

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

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
        self.requires("libiconv/1.17")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        if self._is_msvc or self._is_clang_cl:
            self.build_requires("automake/1.16.5")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
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
        if self._is_msvc or self._is_clang_cl:
            # INSTALL.windows: Native binaries, built using the MS Visual C/C++ tool chain.
            build = False
            if self.settings.arch == "x86":
                host = "i686-w64-mingw32"
                rc = "windres --target=pe-i386"
            elif self.settings.arch == "x86_64":
                host = "x86_64-w64-mingw32"
                rc = "windres --target=pe-x86-64"
            cl = "cl" if self._is_msvc else os.environ.get("CC", 'clang-cl')
            lib = "lib" if self._is_msvc else os.environ.get('AR', "llvm-lib")
            link = "link" if self._is_msvc else os.environ.get("LD", "lld-link")
            args.extend(["CC=%s %s -nologo" % (tools.unix_path(self._user_info_build["automake"].compile), cl),
                         "LD=%s" % link,
                         "NM=dumpbin -symbols",
                         "STRIP=:",
                         "AR=%s %s" % (tools.unix_path(self._user_info_build["automake"].ar_lib), lib),
                         "RANLIB=:"])
            if rc:
                args.extend(['RC=%s' % rc, 'WINDRES=%s' % rc])
        with tools.vcvars(self.settings) if (self._is_msvc or self._is_clang_cl) else tools.no_op():
            with tools.environment_append(VisualStudioBuildEnvironment(self).vars) if (self._is_msvc or self._is_clang_cl) else tools.no_op():
                with tools.chdir(os.path.join(self._source_subfolder, self._gettext_folder)):
                    env_build = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
                    if self._is_msvc:
                        if not (self.settings.compiler == "Visual Studio" and
                                tools.Version(self.settings.compiler.version) < "12"):
                            env_build.flags.append("-FS")
                    env_build.configure(args=args, build=build, host=host)
                    env_build.make(self._make_args)

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*gnuintl*.dll", dst="bin", src=self._source_subfolder, keep_path=False)
        self.copy(pattern="*gnuintl*.lib", dst="lib", src=self._source_subfolder, keep_path=False)
        self.copy(pattern="*gnuintl*.a", dst="lib", src=self._source_subfolder, keep_path=False)
        self.copy(pattern="*gnuintl*.so*", dst="lib", src=self._source_subfolder, keep_path=False, symlinks=True)
        self.copy(pattern="*gnuintl*.dylib", dst="lib", src=self._source_subfolder, keep_path=False, symlinks=True)
        self.copy(pattern="*libgnuintl.h", dst="include", src=self._source_subfolder, keep_path=False)
        tools.rename(os.path.join(self.package_folder, "include", "libgnuintl.h"),
                     os.path.join(self.package_folder, "include", "libintl.h"))
        if (self._is_msvc or self._is_clang_cl) and self.options.shared:
            tools.rename(os.path.join(self.package_folder, "lib", "gnuintl.dll.lib"),
                         os.path.join(self.package_folder, "lib", "gnuintl.lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "Intl")
        self.cpp_info.set_property("cmake_target_name", "Intl::Intl")
        self.cpp_info.libs = ["gnuintl"]
        if tools.is_apple_os(self.settings.os):
            self.cpp_info.frameworks.append("CoreFoundation")

        self.cpp_info.names["cmake_find_package"] = "Intl"
        self.cpp_info.names["cmake_find_package_multi"] = "Intl"
