from functools import lru_cache
from os import environ, path

from conan import ConanFile
from conan.errors import ConanException
from conan.tools.build import build_jobs
from conan.tools.env import Environment
from conan.tools.files import get, apply_conandata_patches, copy, rmdir, mkdir, save
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.scm import Version
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
                                                accepted_extensions=("sh", ))
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
        autotool = AutotoolsWinBash(self)
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
        self.runenv_info.prepend_path("PATH", bin_dir)
        self.env_info.PATH.append(bin_dir)

        # M4 environment variable is used by a lot of scripts as a way to override a hard-coded embedded m4 path
        m4_bin = path.join(bin_dir, "m4")
        self.output.info(f"Setting M4 environment variable: {m4_bin}")
        self.buildenv_info.define_path("M4", m4_bin)
        self.runenv_info.define_path("M4", m4_bin)
        self.env_info.M4 = m4_bin

        m4_bin_conf_key = "user.m4:bin"
        self.output.info(f"Defining path to M4 binary in configuration as `{m4_bin_conf_key}` with value: {m4_bin}")
        self.conf_info.define(m4_bin_conf_key, m4_bin)
