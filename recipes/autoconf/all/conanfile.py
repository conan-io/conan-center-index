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
    name = "autoconf"
    description = "Autoconf is an extensible package of M4 macros that produce shell scripts to automatically configure software source code packages"
    license =  ("GPL-2.0-or-later", "GPL-3.0-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/autoconf/"
    topics = ("autoconf", "configure", "build")
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        # TODO: Remove for Conan v2
        return getattr(self, "settings_build", self.settings)

    @property
    def win_bash(self):
        return self._settings_build.os == "Windows"

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def package_id(self):
        del self.info.settings.compiler

    def layout(self):
        basic_layout(self, src_folder="autoconf")

    def build_requirements(self):
        if self.win_bash and not os.environ.get("CONAN_BASH_PATH"):
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
            tc.configure_args.extend(["gl_cv_func_printf_directive_n=no", "gl_cv_func_snprintf_directive_n=no", "gl_cv_func_snprintf_directive_n=no"])

            tc.extra_cxxflags.append("-FS")
            if self.settings.build_type in ("Debug", "RelWithDebInfo"):
                tc.ldflags.append("-PDB")

        elif self.settings.compiler == "clang" and Version(self.version) < "1.4.19":
            tc.cxxflags.extend(["-rtlib=compiler-rt", "-Wno-unused-command-line-argument"])

        if self.settings.os == "Windows":
            tc.configure_args.extend(["ac_cv_func__set_invalid_parameter_handler=yes"])

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
        self.run(f"chmod +x {unix_path(self, self.generators_path.joinpath('help2man', 'help2man'))}")  #ensure that help2man can run
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
        self.env_info.M4.append(str(m4_bin))
        self.buildenv_info.define_path("M4", str(m4_bin))

        m4_bin_conf_key = "tools.m4:bin"
        self.output.info(f"Defining path to M4 binary in configuration as `{m4_bin_conf_key}` with value: {m4_bin}")
        self.conf_info.define(m4_bin_conf_key, str(m4_bin))




























from functools import lru_cache
from os import environ, path

from conan import ConanFile
from conan.errors import ConanException
from conan.tools.build import build_jobs
from conan.tools.files import get, apply_conandata_patches, copy, rmdir
from conan.tools.gnu import Autotools
from conan.tools.layout import basic_layout
from conan.tools.microsoft import unix_path
from conans.client import subsystems
from conans.client.build import join_arguments
from conans.client.subsystems import subsystem_path, deduce_subsystem, MSYS2, _escape_windows_cmd
from conans.tools import args_to_string

required_conan_version = ">=1.50.0"


# Duck typing the subsystems._windows_bash_wrapper method, so it wil use the correct path for activation of the environments in the bash subsystem
# issue conan-io/conan#11980
def _windows_bash_wrapper_fix(conanfile, command, env, envfiles_folder):
    from conan.tools.env import Environment
    from conan.tools.env.environment import environment_wrap_command
    """ Will wrap a unix command inside a bash terminal It requires to have MSYS2, CYGWIN, or WSL"""

    subsystem = conanfile.conf.get("tools.microsoft.bash:subsystem")
    shell_path = conanfile.conf.get("tools.microsoft.bash:path")
    if not subsystem or not shell_path:
        raise ConanException("The config 'tools.microsoft.bash:subsystem' and "
                             "'tools.microsoft.bash:path' are "
                             "needed to run commands in a Windows subsystem")
    env = env or []
    if subsystem == MSYS2:
        # Configure MSYS2 to inherith the PATH
        msys2_mode_env = Environment()
        _msystem = {"x86": "MINGW32"}.get(conanfile.settings.get_safe("arch"), "MINGW64")
        msys2_mode_env.define("MSYSTEM", _msystem)
        msys2_mode_env.define("MSYS2_PATH_TYPE", "inherit")
        msys2_mode_bat = path.join(conanfile.generators_folder, "msys2_mode.bat")
        msys2_mode_env.vars(conanfile, "build").save_bat(msys2_mode_bat)
        env.append(msys2_mode_bat)

    wrapped_shell = '"%s"' % shell_path if " " in shell_path else shell_path
    wrapped_shell = environment_wrap_command(env, envfiles_folder, wrapped_shell,
                                             accepted_extensions=("bat", "ps1"))

    # Wrapping the inside_command enable to prioritize our environment, otherwise /usr/bin go
    # first and there could be commands that we want to skip
    wrapped_user_cmd = environment_wrap_command(env, envfiles_folder, command,
                                                subsystem=subsystem,  # Fix from main branch, see issue conan-io/conan#11980
                                                accepted_extensions=("sh",))
    wrapped_user_cmd = _escape_windows_cmd(wrapped_user_cmd)

    final_command = '{} -c {}'.format(wrapped_shell, wrapped_user_cmd)
    return final_command


subsystems._windows_bash_wrapper = _windows_bash_wrapper_fix


# Fixing Autotools on Windows with a subsystem
class AutotoolsWinBash(Autotools):

    def configure(self, build_script_folder=None, args=None):
        """
        http://jingfenghanmax.blogspot.com.es/2010/09/configure-with-host-target-and-build.html
        https://gcc.gnu.org/onlinedocs/gccint/Configure-Terms.html
        """
        script_folder = path.join(self._conanfile.source_folder, build_script_folder) \
            if build_script_folder else self._conanfile.source_folder

        configure_args = []
        configure_args.extend(args or [])

        self._configure_args = "{} {}".format(self._configure_args, args_to_string(configure_args))

        configure_cmd = "{}/configure".format(script_folder)
        subsystem = deduce_subsystem(self._conanfile, scope="build")
        configure_cmd = subsystem_path(subsystem, configure_cmd)
        cmd = '"{}" {}'.format(configure_cmd, self._configure_args)
        self._conanfile.output.info("Calling:\n > %s" % cmd)
        self._conanfile.run(cmd, run_environment=True)

    def make(self, target=None, args=None):
        make_program = self._conanfile.conf.get("tools.gnu:make_program",
                                                default="mingw32-make" if self._use_win_mingw() else "make")
        str_args = self._make_args
        str_extra_args = " ".join(args) if args is not None else ""
        jobs = ""
        if "-j" not in str_args and "nmake" not in make_program.lower():
            njobs = build_jobs(self._conanfile)
            if njobs:
                jobs = "-j{}".format(njobs)
        command = join_arguments([make_program, target, str_args, str_extra_args, jobs])
        self._conanfile.run(command, run_environment=True)


class AutoconfConan(ConanFile):
    name = "autoconf"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/autoconf/"
    description = "Autoconf is an extensible package of M4 macros that produce shell scripts to automatically configure software source code packages"
    topics = ("autoconf", "configure", "build")
    license = ("GPL-2.0-or-later", "GPL-3.0-or-later")
    settings = "os", "arch", "compiler", "build_type"
    generators = "AutotoolsDeps", "AutotoolsToolchain", "VirtualBuildEnv"
    win_bash = True

    exports_sources = "patches/*"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _datarootdir(self):
        return path.join(self.package_folder, "bin", "share")

    @property
    def _autoconf_datarootdir(self):
        return path.join(self._datarootdir, "autoconf")

    def package_id(self):
        self.info.clear()

    def requirements(self):
        self.requires("m4/1.4.19")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not environ.get("CONAN_BASH_PATH"):
            self.tool_requires("msys2/cci.latest")
        if hasattr(self, "settings_build"):
            self.tool_requires("m4/1.4.19")

    def layout(self):
        basic_layout(self, src_folder="source")
        self.cpp.package.includedirs = []  # KB-H071: It is a tool that doesn't contain headers, removing the include directory.

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @lru_cache(1)
    def _autotools(self):
        autotool = AutotoolsWinBash(self)
        autotool.configure()
        autotool.make()
        return autotool

    def build(self):
        apply_conandata_patches(self)
        self._autotools()

    def package(self):
        autotools = self._autotools()
        # KB-H013 we're packaging an application, place everything under bin
        autotools.install(args=[f"DESTDIR={unix_path(self, path.join(self.package_folder, 'bin'))}"])
        copy(self, "COPYING*", src=self.source_folder, dst=path.join(self.package_folder, "licenses"))
        rmdir(self, path.join(self._datarootdir, "info"))
        rmdir(self, path.join(self._datarootdir, "man"))

    def _set_env(self, var_name, var_path):
        self.output.info(f"Setting {var_name} to {var_path}")
        self.buildenv_info.define_path(var_name, var_path)
        self.runenv_info.define_path(var_name, var_path)
        setattr(self.env_info, var_name, var_path)

    def package_info(self):
        # KB-H013 we're packaging an application, hence the nested bin
        bin_dir = path.join(self.package_folder, "bin", "bin")
        self.output.info(f"Appending PATH env var with : {bin_dir}")
        self.buildenv_info.prepend_path("PATH", bin_dir)
        self.runenv_info.prepend_path("PATH", bin_dir)
        self.env_info.PATH.append(bin_dir)

        for var in [("AC_MACRODIR", self._autoconf_datarootdir),
                    ("AUTOCONF", path.join(bin_dir, "autoconf")),
                    ("AUTORECONF", path.join(bin_dir, "autoreconf")),
                    ("AUTOHEADER", path.join(bin_dir, "autoheader")),
                    ("AUTOM4TE", path.join(bin_dir, "autom4te")),
                    ("AUTOM4TE_PERLLIBDIR", self._autoconf_datarootdir)]:
            self._set_env(*var)
