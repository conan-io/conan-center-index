from conans import ConanFile, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import contextlib
import os

required_conan_version = ">=1.33.0"


class GetTextConan(ConanFile):
    name = "gettext"
    description = "An internationalization and localization system for multilingual programs"
    topics = ("gettext", "intl", "libintl", "i18n")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/gettext"
    license = "GPL-3.0-or-later"
    settings = "os", "arch", "compiler"

    exports_sources = "patches/*"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("libiconv/1.17")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        if self._is_msvc:
            self.build_requires("automake/1.16.5")

    def validate(self):
        if tools.Version(self.version) < "0.21" and self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("MSVC builds of gettext for versions < 0.21 are not supported.")  # FIXME: it used to be possible. What changed?

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            env = {
                "CC": "{} cl -nologo".format(tools.unix_path(self._user_info_build["automake"].compile)),
                "LD": "link -nologo",
                "NM": "dumpbin -symbols",
                "STRIP": ":",
                "AR": "{} lib".format(tools.unix_path(self._user_info_build["automake"].ar_lib)),
                "RANLIB": ":",
            }
            with tools.vcvars(self):
                with tools.environment_append(VisualStudioBuildEnvironment(self).vars):
                    with tools.environment_append(env):
                        yield
        else:
            yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.libs = []
        libiconv_prefix = tools.unix_path(self.deps_cpp_info["libiconv"].rootpath)
        args = [
            "HELP2MAN=/bin/true",
            "EMACS=no",
            "--datarootdir={}".format(tools.unix_path(os.path.join(self.package_folder, "res"))),
            "--with-libiconv-prefix={}".format(libiconv_prefix),
            "--disable-shared",
            "--disable-static",
            "--disable-nls",
            "--disable-dependency-tracking",
            "--enable-relocatable",
            "--disable-c++",
            "--disable-java",
            "--disable-csharp",
            "--disable-libasprintf",
            "--disable-curses",
        ]
        build = None
        host = None
        if self._is_msvc:
            rc = None
            self._autotools.flags.append("-FS")
            # INSTALL.windows: Native binaries, built using the MS Visual C/C++ tool chain.
            build = False
            if self.settings.arch == "x86":
                host = "i686-w64-mingw32"
                rc = "windres --target=pe-i386"
            elif self.settings.arch == "x86_64":
                host = "x86_64-w64-mingw32"
                rc = "windres --target=pe-x86-64"
            if rc:
                args.extend([
                    "RC={}".format(rc),
                    "WINDRES={}".format(rc),
                ])
        self._autotools.configure(args=args, configure_dir=self._source_subfolder, build=build, host=host)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        tools.replace_in_file(os.path.join(self._source_subfolder, "gettext-tools", "misc", "autopoint.in"), "@prefix@", "$GETTEXT_ROOT_UNIX")
        tools.replace_in_file(os.path.join(self._source_subfolder, "gettext-tools", "misc", "autopoint.in"), "@datarootdir@", "$prefix/res")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="COPYING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "lib"))
        tools.rmdir(os.path.join(self.package_folder, "include"))
        tools.rmdir(os.path.join(self.package_folder, "share", "doc"))
        tools.rmdir(os.path.join(self.package_folder, "share", "info"))
        tools.rmdir(os.path.join(self.package_folder, "share", "man"))

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        aclocal = tools.unix_path(os.path.join(self.package_folder, "res", "aclocal"))
        self.output.info("Appending AUTOMAKE_CONAN_INCLUDES environment variable: {}".format(aclocal))
        self.env_info.AUTOMAKE_CONAN_INCLUDES.append(aclocal)

        autopoint = tools.unix_path(os.path.join(self.package_folder, "bin", "autopoint"))
        self.output.info("Setting AUTOPOINT environment variable: {}".format(autopoint))
        self.env_info.AUTOPOINT = autopoint

        self.env_info.GETTEXT_ROOT_UNIX = tools.unix_path(self.package_folder)
