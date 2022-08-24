from conans import ConanFile, AutoToolsBuildEnvironment, tools
import contextlib
import os

required_conan_version = ">=1.33.0"


class BisonConan(ConanFile):
    name = "bison"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/bison/"
    description = "Bison is a general-purpose parser generator"
    topics = ("bison", "parser")
    license = "GPL-3.0-or-later"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    exports_sources = "patches/*"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("m4/1.4.19")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        if self.settings.compiler == "Visual Studio":
            self.build_requires("automake/1.16.4")
        if self.settings.os != "Windows":
            self.build_requires("flex/2.6.4")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self):
                env = {
                    "CC": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                    "CXX": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                    "CFLAGS": "-{}".format(self.settings.compiler.runtime),
                    "LD": "link",
                    "NM": "dumpbin -symbols",
                    "STRIP": ":",
                    "AR": "{} lib".format(tools.unix_path(self.deps_user_info["automake"].ar_lib)),
                    "RANLIB": ":",
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    @property
    def _datarootdir(self):
        return os.path.join(self.package_folder, "res")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        args = [
            "--enable-relocatable",
            "--disable-nls",
            "--datarootdir={}".format(os.path.join(self._datarootdir).replace("\\", "/")),
        ]
        host, build = None, None
        if self.settings.os == "Windows":
            self._autotools.defines.append("_WINDOWS")
        if self.settings.compiler == "apple-clang":
            args.append("gl_cv_compiler_check_decl_option=")
        if self.settings.compiler == "Visual Studio":
            # Avoid a `Assertion Failed Dialog Box` during configure with build_type=Debug
            # Visual Studio does not support the %n format flag:
            # https://docs.microsoft.com/en-us/cpp/c-runtime-library/format-specification-syntax-printf-and-wprintf-functions
            # Because the %n format is inherently insecure, it is disabled by default. If %n is encountered in a format string,
            # the invalid parameter handler is invoked, as described in Parameter Validation. To enable %n support, see _set_printf_count_output.
            args.extend(["gl_cv_func_printf_directive_n=no", "gl_cv_func_snprintf_directive_n=no", "gl_cv_func_snprintf_directive_n=no"])
            self._autotools.flags.append("-FS")
            host, build = False, False
        self._autotools.configure(args=args, configure_dir=self._source_subfolder, host=host, build=build)
        return self._autotools

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

        if self.settings.os == "Windows":
            # replace embedded unix paths by windows paths
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "Makefile.in"),
                                  "echo '#define BINDIR \"$(bindir)\"';",
                                  "echo '#define BINDIR \"$(shell cygpath -m \"$(bindir)\")\"';")
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "Makefile.in"),
                                  "echo '#define PKGDATADIR \"$(pkgdatadir)\"';",
                                  "echo '#define PKGDATADIR \"$(shell cygpath -m \"$(pkgdatadir)\")\"';")
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "Makefile.in"),
                                  "echo '#define DATADIR \"$(datadir)\"';",
                                  "echo '#define DATADIR \"$(shell cygpath -m \"$(datadir)\")\"';")
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "Makefile.in"),
                                  "echo '#define DATAROOTDIR \"$(datarootdir)\"';",
                                  "echo '#define DATAROOTDIR \"$(shell cygpath -m \"$(datarootdir)\")\"';")

        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "Makefile.in"),
                              "dist_man_MANS = $(top_srcdir)/doc/bison.1",
                              "dist_man_MANS =")
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "src", "yacc.in"),
                              "@prefix@",
                              "${}_ROOT".format(self.name.upper()))
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "src", "yacc.in"),
                              "@bindir@",
                              "${}_ROOT/bin".format(self.name.upper()))

    def build(self):
        self._patch_sources()
        with self._build_context():
            env_build = self._configure_autotools()
            env_build.make()

    def package(self):
        with self._build_context():
            env_build = self._configure_autotools()
            env_build.install()
            self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)

        if self.settings.compiler == "Visual Studio":
            os.rename(os.path.join(self.package_folder, "lib", "liby.a"),
                      os.path.join(self.package_folder, "lib", "y.lib"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libs = ["y"]

        self.output.info("Setting BISON_ROOT environment variable: {}".format(self.package_folder))
        self.env_info.BISON_ROOT = self.package_folder.replace("\\", "/")

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
        pkgdir = os.path.join(self._datarootdir, "bison")
        self.output.info("Setting the BISON_PKGDATADIR environment variable: {}".format(pkgdir))
        self.env_info.BISON_PKGDATADIR = pkgdir

        # yacc is a shell script, so requires a shell (such as bash)
        self.user_info.YACC = os.path.join(self.package_folder, "bin", "yacc").replace("\\", "/")
