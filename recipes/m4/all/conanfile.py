from conan import ConanFile, tools
from conans import AutoToolsBuildEnvironment
from contextlib import contextmanager
import functools
import os

required_conan_version = ">=1.33.0"


class M4Conan(ConanFile):
    name = "m4"
    description = "GNU M4 is an implementation of the traditional Unix macro processor"
    topics = ("macro", "preprocessor")
    homepage = "https://www.gnu.org/software/m4/"
    url = "https://github.com/conan-io/conan-center-index"
    license = "GPL-3.0-only"
    settings = "os", "arch", "compiler", "build_type"

    exports_sources = "patches/*.patch",

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio" or self.settings.compiler == "msvc"

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_autotools(self):
        conf_args = []
        autotools = AutoToolsBuildEnvironment(self, win_bash=self._settings_build.os == "Windows")
        build_canonical_name = None
        host_canonical_name = None
        if self._is_msvc:
            # The somewhat older configure script of m4 does not understand the canonical names of Visual Studio
            build_canonical_name = False
            host_canonical_name = False
            autotools.flags.append("-FS")
            # Avoid a `Assertion Failed Dialog Box` during configure with build_type=Debug
            # Visual Studio does not support the %n format flag:
            # https://docs.microsoft.com/en-us/cpp/c-runtime-library/format-specification-syntax-printf-and-wprintf-functions
            # Because the %n format is inherently insecure, it is disabled by default. If %n is encountered in a format string,
            # the invalid parameter handler is invoked, as described in Parameter Validation. To enable %n support, see _set_printf_count_output.
            conf_args.extend(["gl_cv_func_printf_directive_n=no", "gl_cv_func_snprintf_directive_n=no", "gl_cv_func_snprintf_directive_n=no"])
            if self.settings.build_type in ("Debug", "RelWithDebInfo"):
                autotools.link_flags.append("-PDB")
        elif self.settings.compiler == "clang":
            if tools.scm.Version(self.version) < "1.4.19":
                autotools.flags.extend(["-rtlib=compiler-rt", "-Wno-unused-command-line-argument"])
        if self.settings.os == 'Windows':
            conf_args.extend(["ac_cv_func__set_invalid_parameter_handler=yes"])

        autotools.configure(args=conf_args, configure_dir=self._source_subfolder, build=build_canonical_name, host=host_canonical_name)
        return autotools

    @contextmanager
    def _build_context(self):
        env = {"PATH": [os.path.abspath(self._source_subfolder)]}
        if self._is_msvc:
            with tools.vcvars(self.settings):
                env.update({
                    "AR": "{}/build-aux/ar-lib lib".format(tools.microsoft.unix_path(self, self._source_subfolder)),
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
            with tools.environment_append(env):
                yield

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    def build(self):
        with tools.files.chdir(self, self._source_subfolder):
            tools.files.save(self, "help2man", '#!/usr/bin/env bash\n:')
            if os.name == 'posix':
                os.chmod("help2man", os.stat("help2man").st_mode | 0o111)
        self._patch_sources()
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()
            if tools.get_env("CONAN_RUN_TESTS", False):
                self.output.info("Running m4 checks...")
                with tools.files.chdir(self, "tests"):
                    autotools.make(target="check")

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        bin_ext = ".exe" if self.settings.os == "Windows" else ""
        m4_bin = os.path.join(self.package_folder, "bin", "m4{}".format(bin_ext)).replace("\\", "/")

        # M4 environment variable is used by a lot of scripts as a way to override a hard-coded embedded m4 path
        self.output.info("Setting M4 environment variable: {}".format(m4_bin))
        self.env_info.M4 = m4_bin
