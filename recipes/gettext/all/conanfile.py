from conans import ConanFile, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment, tools
from contextlib import contextmanager
import os


class GetTextConan(ConanFile):
    name = "gettext"
    description = "An internationalization and localization system for multilingual programs"
    topics = ("conan", "gettext", "intl", "libintl", "i18n")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/gettext"
    license = "GPL-3.0-or-later"
    settings = "os_build", "arch_build", "compiler"
    exports_sources = ["patches/*.patch"]

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("libiconv/1.16")

    def package_id(self):
        self.info.include_build_settings()
        del self.info.settings.compiler

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/20200517")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "gettext-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    @contextmanager
    def _build_context(self):
        with tools.chdir(os.path.join(self._source_subfolder)):
            if self._is_msvc:
                with tools.vcvars(self.settings):
                    with tools.environment_append(VisualStudioBuildEnvironment(self).vars):
                        yield
            else:
                yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        libiconv_prefix = tools.unix_path(self.deps_cpp_info["libiconv"].rootpath)
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
        args.extend(["--disable-shared", "--enable-static"])
        if self._is_msvc:
            # INSTALL.windows: Native binaries, built using the MS Visual C/C++ tool chain.
            build = False
            if self.settings.arch_build == "x86":
                host = "i686-w64-mingw32"
                rc = "windres --target=pe-i386"
            elif self.settings.arch_build == "x86_64":
                host = "x86_64-w64-mingw32"
                rc = "windres --target=pe-x86-64"
            args.extend(["CC={} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                         "LD=link",
                         "NM=dumpbin -symbols",
                         "STRIP=:",
                         "AR={} lib".format(tools.unix_path(self.deps_user_info["automake"].ar_lib)),
                         "RANLIB=:"])
            if rc:
                args.extend(["RC=%s" % rc, "WINDRES=%s" % rc])
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        if self._is_msvc:
            self._autotools.flags.append("-FS")
        self._autotools.configure(args=args, build=build, host=host)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        with self._build_context():
            env_build = self._configure_autotools()
            env_build.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        with self._build_context():
            env_build = self._configure_autotools()
            env_build.install()
        tools.rmdir(os.path.join(self.package_folder, "include"))
        tools.rmdir(os.path.join(self.package_folder, "lib"))
        tools.mkdir(os.path.join(self.package_folder, "bin", "share"))
        os.rename(os.path.join(self.package_folder, "share", "aclocal"),
                  os.path.join(self.package_folder, "bin", "share", "aclocal"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        gettext_aclocal = tools.unix_path(os.path.join(self.package_folder, "bin", "share", "aclocal"))
        self.output.info("Appending ACLOCAL_PATH environment variable: {}".format(gettext_aclocal))
        self.env_info.ACLOCAL_PATH.append(gettext_aclocal)
