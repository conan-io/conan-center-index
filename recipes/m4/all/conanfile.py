from conans import ConanFile, tools, AutoToolsBuildEnvironment
from contextlib import contextmanager
import os


class M4Conan(ConanFile):
    name = "m4"
    description = "GNU M4 is an implementation of the traditional Unix macro processor"
    topics = ("conan", "m4", "macro", "macro processor")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/m4/"
    license = "GPL-3.0-only"
    exports_sources = ["patches/*.patch"]
    settings = "os", "arch", "compiler", "build_type"

    _autotools = None
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    @property
    def _is_clang(self):
        return str(self.settings.compiler).endswith("clang")

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/20200517")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("m4-" + self.version, self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        conf_args = []
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        build_canonical_name = None
        host_canonical_name = None
        if self.settings.compiler == "Visual Studio":
            # The somewhat older configure script of m4 does not understand the canonical names of Visual Studio
            build_canonical_name = False
            host_canonical_name = False
            self._autotools.flags.append("-FS")
            # Avoid a `Assertion Failed Dialog Box` during configure with build_type=Debug
            # Visual Studio does not support the %n format flag:
            # https://docs.microsoft.com/en-us/cpp/c-runtime-library/format-specification-syntax-printf-and-wprintf-functions
            # Because the %n format is inherently insecure, it is disabled by default. If %n is encountered in a format string,
            # the invalid parameter handler is invoked, as described in Parameter Validation. To enable %n support, see _set_printf_count_output.
            conf_args.extend(["gl_cv_func_printf_directive_n=no", "gl_cv_func_snprintf_directive_n=no", "gl_cv_func_snprintf_directive_n=no"])
            if self.settings.build_type in ("Debug", "RelWithDebInfo"):
                self._autotools.link_flags.append("-PDB")
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder, build=build_canonical_name, host=host_canonical_name)
        return self._autotools

    @contextmanager
    def _build_context(self):
        env = {}
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                env.update({
                    "AR": "{}/build-aux/ar-lib lib".format(tools.unix_path(self._source_subfolder)),
                    "CC": "cl -nologo",
                    "CXX": "cl -nologo",
                    "LD": "link",
                    "NM": "dumpbin -symbols",
                    "OBJDUMP": ":",
                    "RANLIB": ":",
                    "STRIP": ":",
                })
                with tools.environment_append(env):
                    yield
        else:
            if self._is_clang:
                env["CFLAGS"] = "-rtlib=compiler-rt"
            with tools.environment_append(env):
                yield

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()
            if bool(os.environ.get("CONAN_RUN_TESTS", "")):
                self.output.info("Running m4 checks...")
                with tools.chdir("tests"):
                    autotools.make(target="check")

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_id(self):
        self.info.include_build_settings()
        del self.info.settings.compiler

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        bin_ext = ".exe" if self.settings.os == "Windows" else ""
        m4_bin = os.path.join(self.package_folder, "bin", "m4{}".format(bin_ext)).replace("\\", "/")

        # M4 environment variable is used by a lot of scripts as a way to override a hard-coded embedded m4 path
        self.output.info("Setting M4 environment variable: {}".format(m4_bin))
        self.env_info.M4 = m4_bin
