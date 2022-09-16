import os

from conan import ConanFile
from conan.tools.env import VirtualBuildEnv, Environment
from conan.tools.files import copy, get, rmdir, apply_conandata_patches, mkdir, save
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.scm import Version

required_conan_version = ">=1.51.3"


class M4Conan(ConanFile):
    name = "m4"
    description = "GNU M4 is an implementation of the traditional Unix macro processor"
    license = "GPL-3.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/m4/"
    topics = ("macro", "preprocessor")
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        # TODO: Remove for Conan v2
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def package_id(self):
        del self.info.settings.compiler

    def configure(self):
        self.win_bash = self._settings_build.os == "Windows"

    def layout(self):
        basic_layout(self, src_folder="m4")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", default=False, check_type=bool):
            self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        # mimic help2man and add make sure it can be found on the path
        mkdir(self, self.generators_path.joinpath("help2man"))
        save(self, self.generators_path.joinpath("help2man", "help2man"), '#!/usr/bin/env bash\n:')

        help2man_env = Environment()
        help2man_env.append_path("PATH", str(self.generators_path.joinpath("help2man")))
        env = help2man_env.vars(self, scope="build")
        env.save_script("conanhelp2man")

        tc = AutotoolsToolchain(self)

        if is_msvc(self):
            # Avoid a `Assertion Failed Dialog Box` during configure with build_type=Debug
            # Visual Studio does not support the %n format flag:
            # https://docs.microsoft.com/en-us/cpp/c-runtime-library/format-specification-syntax-printf-and-wprintf-functions
            # Because the %n format is inherently insecure, it is disabled by default. If %n is encountered in a format string,
            # the invalid parameter handler is invoked, as described in Parameter Validation. To enable %n support, see _set_printf_count_output.
            tc.configure_args.extend([
                "gl_cv_func_printf_directive_n=no",
                "gl_cv_func_snprintf_directive_n=no",
            ])
            if self.settings.os == "Windows":
                tc.configure_args.extend([
                    "ac_cv_func__set_invalid_parameter_handler=yes",
                ])

            tc.extra_cxxflags.append("-FS")
            tc.extra_cflags.append("-FS")
            if self.settings.build_type in ("Debug", "RelWithDebInfo"):
                tc.ldflags.append("-PDB")

        elif self.settings.compiler == "clang" and Version(self.version) < "1.4.19":
            tc.extra_cxxflags.extend([
                "-rtlib=compiler-rt",
                "-Wno-unused-command-line-argument",
            ])
            tc.extra_cflags.extend([
                "-rtlib=compiler-rt",
                "-Wno-unused-command-line-argument",
            ])

        env = tc.environment()
        if is_msvc(self):
            env.define("AR", f"{unix_path(self, str(self.source_path.joinpath('build-aux', 'ar-lib')))} lib")
            env.define("LD", "link -nologo")
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
        tc.generate(env)

        ms = VirtualBuildEnv(self)
        ms.generate(scope="build")

    def build(self):
        self.run(f"chmod +x {unix_path(self, self.generators_path.joinpath('help2man', 'help2man'))}")  # ensure that help2man can run
        apply_conandata_patches(self)

        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])  # Need to specify the `DESTDIR` as a Unix path, aware of the subsystem

        copy(self, "COPYING*", src=self.source_folder, dst=self.package_path.joinpath("licenses"))
        rmdir(self, self.package_path.joinpath("share"))

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []

        bin_path = self.package_path.joinpath("bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(str(bin_path))

        ext = ".exe" if self.settings.os == "Windows" else ""
        m4_bin = bin_path.joinpath(f"m4{ext}")
        self.output.info(f"Define M4 with {m4_bin}")
        self.env_info.M4 = str(m4_bin)
        self.runenv_info.define_path("M4", str(m4_bin))

        m4_bin_conf_key = "tools.m4:bin"
        self.output.info(f"Defining path to M4 binary in configuration as `{m4_bin_conf_key}` with value: {m4_bin}")
        self.conf_info.define(m4_bin_conf_key, str(m4_bin))
