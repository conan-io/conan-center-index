from functools import lru_cache
from os import environ, path, listdir

from conan import ConanFile
from conan.errors import ConanException
from conan.tools.build import build_jobs
from conan.tools.files import get, apply_conandata_patches, rmdir, copy, replace_in_file, rename
from conan.tools.gnu import Autotools
from conan.tools.layout import basic_layout
from conan.tools.microsoft import unix_path
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


class AutomakeConan(ConanFile):
    name = "automake"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/automake/"
    description = "Automake is a tool for automatically generating Makefile.in files compliant with the GNU Coding Standards."
    topics = ("conan", "automake", "configure", "build")
    license = ("GPL-2.0-or-later", "GPL-3.0-or-later")
    settings = "os", "arch", "compiler", "build_type"
    generators = "AutotoolsDeps", "AutotoolsToolchain", "VirtualBuildEnv"
    win_bash = True

    exports_sources = "patches/*"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def requirements(self):
        self.requires("autoconf/2.71")
        self.requires("m4/1.4.19")

    def build_requirements(self):
        if hasattr(self, "settings_build"):
            self.tool_requires("autoconf/2.71")
            self.tool_requires("m4/1.4.19")
        if self._settings_build.os == "Windows" and not environ.get("CONAN_BASH_PATH"):
            self.tool_requires("msys2/cci.latest")

    def package_id(self):
        del self.info.settings.arch
        del self.info.settings.compiler
        del self.info.settings.build_type

    def layout(self):
        basic_layout(self, src_folder="source")
        self.cpp.package.includedirs = []  # KB-H071: It is a tool that doesn't contain headers, removing the include directory.

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _datarootdir(self):
        return path.join(self.package_folder, "bin", "share")

    @property
    def _automake_libdir(self):
        version = Version(self.version)
        return path.join(self._datarootdir, f"automake-{version.major}.{version.minor}")

    @lru_cache(1)
    def _autotools(self):
        autotool = AutotoolsWinBash(self)
        autotool.configure()
        autotool.make()
        return autotool

    def build(self):
        apply_conandata_patches(self)
        if self.settings.os == "Windows":
            # tracing using m4 on Windows returns Windows paths => use cygpath to convert to unix paths
            replace_in_file(self, path.join(self.source_path, "bin", "aclocal.in"),
                            "          $map_traced_defs{$arg1} = $file;",
                            "          $file = `cygpath -u $file`;\n"
                            "          $file =~ s/^\\s+|\\s+$//g;\n"
                            "          $map_traced_defs{$arg1} = $file;")

        _ = self._autotools()

    def package(self):
        autotools = self._autotools()
        # KB-H013 we're packaging an application, place everything under bin
        autotools.install(args=[f"DESTDIR={unix_path(self, path.join(self.package_folder, 'bin'))}"])

        if self._settings_build.os == "Windows":
            bin_dir = path.join(self.package_folder, "bin", "bin")
            for filename in listdir(bin_dir):
                fullpath = path.join(bin_dir, filename)
                if not path.isfile(fullpath):
                    continue
                rename(self, fullpath, f"{fullpath}.exe")

        copy(self, "COPYING*", src=self.source_folder, dst=path.join(self.package_folder, "licenses"))
        rmdir(self, path.join(self._datarootdir, "info"))
        rmdir(self, path.join(self._datarootdir, "man"))
        rmdir(self, path.join(self._datarootdir, "doc"))

    def _set_env(self, var_name, var_path):
        self.output.info(f"Setting {var_name} to {var_path}")
        self.buildenv_info.define_path(var_name, var_path)
        self.runenv_info.define_path(var_name, var_path)
        setattr(self.env_info, var_name, var_path)

    def package_info(self):
        # KB-H013 we're packaging an application, hence the nested bin
        bin_dir = path.join(self.package_folder, "bin", "bin")
        self.output.info(f"Appending PATH environment variable:: {bin_dir}")
        self.buildenv_info.prepend_path("PATH", bin_dir)
        self.runenv_info.prepend_path("PATH", bin_dir)
        self.env_info.PATH.append(bin_dir)

        bin_ext = ".exe" if self.settings.os == "Windows" else ""
        for var in [("ACLOCAL", path.join(bin_dir, f"aclocal{bin_ext}")),
                    ("AUTOMAKE_DATADIR", self._datarootdir),
                    ("AUTOMAKE_LIBDIR", self._automake_libdir),
                    ("AUTOMAKE_PERLLIBDIR", self._automake_libdir),
                    ("AUTOMAKE", path.join(bin_dir, f"automake{bin_ext}"))]:
            self._set_env(*var)

        compile_bin = path.join(self._automake_libdir, "compile")
        self.output.info(f"Define path to `compile` binary in user_info as: {compile_bin}")
        self.user_info.compile = compile_bin
        compile_conf_key = "tools.automake:compile"
        self.output.info(f"Defining path to `compile` binary in configuration as `{compile_conf_key}` with value: {compile_bin}")
        self.conf_info.define(compile_conf_key, compile_bin)

        ar_lib_bin = path.join(self._automake_libdir, "ar-lib")
        self.output.info(f"Define path to `ar_lib` binary in user_info as: {ar_lib_bin}")
        self.user_info.ar_lib = ar_lib_bin
        ar_lib_conf_key = "tools.automake:ar-lib"
        self.output.info(f"Defining path to `ar-lib` binary in configuration as `{ar_lib_conf_key}` with value: {ar_lib_bin}")
        self.conf_info.define(ar_lib_conf_key, ar_lib_bin)
