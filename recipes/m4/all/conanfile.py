from functools import lru_cache
from os import environ, path

from conan import ConanFile
from conan.tools.env import Environment
from conan.tools.files import get, apply_conandata_patches, copy, rmdir, mkdir, save
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.scm import Version

required_conan_version = ">=1.50.0"


class M4Conan(ConanFile):
    name = "m4"
    description = "GNU M4 is an implementation of the traditional Unix macro processor"
    topics = ("macro", "preprocessor")
    homepage = "https://www.gnu.org/software/m4/"
    url = "https://github.com/conan-io/conan-center-index"
    license = "GPL-3.0-only"
    settings = "os", "arch", "compiler", "build_type"
    generators = "AutotoolsDeps", "VirtualBuildEnv"
    win_bash = True

    exports_sources = "patches/*.patch"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not environ.get("CONAN_BASH_PATH"):
            self.tool_requires("msys2/cci.latest")

    def package_id(self):
        del self.info.settings.compiler

    def layout(self):
        basic_layout(self, src_folder="source")
        self.cpp.package.includedirs = []  # KB-H071: It is a tool that doesn't contain headers, removing the `include` directory.

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        # mimic help2man and add make sure it can be found on the path
        mkdir(self, path.join(self.generators_folder, "help2man"))
        save(self, path.join(self.generators_folder, "help2man", "help2man"), '#!/usr/bin/env bash\n:')

        help2man_env = Environment()
        help2man_env.append_path("PATH", path.join(self.generators_folder, "help2man"))
        env = help2man_env.vars(self, scope="build")
        env.save_script("conanhelp2man")

        at = AutotoolsToolchain(self)
        if is_msvc(self):
            at.cflags.append("-FS")
            at.cxxflags.append("-FS")

            # Avoid a `Assertion Failed Dialog Box` during configure with build_type=Debug
            # Visual Studio does not support the %n format flag:
            # https://docs.microsoft.com/en-us/cpp/c-runtime-library/format-specification-syntax-printf-and-wprintf-functions
            # Because the %n format is inherently insecure, it is disabled by default. If %n is encountered in a format string,
            # the invalid parameter handler is invoked, as described in Parameter Validation. To enable %n support, see _set_printf_count_output.
            at.configure_args.extend(["gl_cv_func_printf_directive_n=no", "gl_cv_func_snprintf_directive_n=no", "gl_cv_func_snprintf_directive_n=no"])

            if self.settings.build_type in ("Debug", "RelWithDebInfo"):
                at.ldflags.append("-PDB")
        elif self.settings.compiler == "clang" and Version(self.version) < "1.4.19":
            at.cflags.extend(["-rtlib=compiler-rt", "-Wno-unused-command-line-argument"])
            at.cxxflags.extend(["-rtlib=compiler-rt", "-Wno-unused-command-line-argument"])

        if self.settings.os == "Windows":
            at.configure_args.extend(["ac_cv_func__set_invalid_parameter_handler=yes"])

        # Needs to be called and set last, otherwise the previous arguments and flags can't be set
        env = at.environment()
        if is_msvc(self):
            env.define("AR", f"{unix_path(self, self.source_folder)}/build-aux/ar-lib lib")
            env.define("LD", "link")  # otherwise configure reports "ld" as its linker. See conan-io/conan#11922
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
        at.generate(env)

    @lru_cache(1)
    def _autotools(self):
        autotool = Autotools(self)
        autotool.configure()
        autotool.make()
        return autotool

    def build(self):
        self.run(f"chmod +x {unix_path(self, path.join(self.generators_folder, 'help2man', 'help2man'))}", run_environment=True)

        apply_conandata_patches(self)
        _ = self._autotools()

    def package(self):
        autotools = self._autotools()
        # KB-H013 we're packaging an application, place everything under bin
        autotools.install(args=[f"DESTDIR={unix_path(self, path.join(self.package_folder, 'bin'))}"])
        copy(self, "COPYING*", src=self.source_folder, dst=path.join(self.package_folder, "licenses"))
        rmdir(self, path.join(self.package_folder, "bin", "share"))

    def package_info(self):
        # KB-H013 we're packaging an application, hence the nested bin
        bin_dir = path.join(self.package_folder, "bin", "bin")
        self.output.info(f"Appending PATH env var with : {bin_dir}")
        self.buildenv_info.prepend_path("PATH", bin_dir)
        self.env_info.PATH.append(bin_dir)

        # M4 environment variable is used by a lot of scripts as a way to override a hard-coded embedded m4 path
        m4_bin = path.join(bin_dir, "m4")
        self.output.info(f"Setting M4 environment variable: {m4_bin}")
        self.buildenv_info.define_path("M4", m4_bin)
        self.env_info.M4 = m4_bin

        m4_bin_conf_key = "user.m4:bin"
        self.output.info(f"Defining path to M4 binary in configuration as `{m4_bin_conf_key}` with value: {m4_bin}")
        self.conf_info.define(m4_bin_conf_key, m4_bin)
