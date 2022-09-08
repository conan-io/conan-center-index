import shutil
from os import environ, path

from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.gnu import Autotools
from conan.tools.microsoft import is_msvc
from conans.client.subsystems import subsystem_path
from conans.tools import vcvars, no_op


def _subsystem(conanfile):
    if conanfile._settings_build.os == "Windows" and not environ.get("CONAN_BASH_PATH"):
        return "msys2"
    return None


def _env_activate_sh_path(conanfile):
    return subsystem_path(_subsystem(conanfile), path.join(conanfile.build_folder, "conanbuild.sh"))


class AutotoolsWinBash(Autotools):
    def configure(self, build_script_folder=None, args=None):
        # Workaround for conan-io/conan#11975
        if self._conanfile._settings_build.os == "Windows" and not environ.get("CONAN_BASH_PATH"):
            from conans.tools import args_to_string
            from conans.client.subsystems import subsystem_path
            script_folder = path.join(self._conanfile.source_folder, build_script_folder) \
                if build_script_folder else self._conanfile.source_folder

            configure_args = []
            configure_args.extend(args or [])

            self._configure_args = "{} {}".format(self._configure_args, args_to_string(configure_args))

            configure_cmd = "{}/configure".format(script_folder)
            configure_cmd = subsystem_path(_subsystem(self._conanfile), configure_cmd)
            cmd = '"{}" {}'.format(configure_cmd, self._configure_args)
            self._conanfile.output.info("Calling:\n > %s" % cmd)
            with vcvars(self._conanfile) if is_msvc(self._conanfile) else no_op():
                self._conanfile.run(
                    '. "{}" && "{}" {}'.format(_env_activate_sh_path(self._conanfile), subsystem_path(_subsystem(self._conanfile), path.join(self._conanfile.build_folder, "configure")),
                                               self._configure_args), run_environment=True, win_bash=True)
        else:
            super(AutotoolsWinBash, self).configure(build_script_folder=build_script_folder, args=args)

    def make(self, target=None, args=None):
        # Workaround for conan-io/conan#11975
        if self._conanfile._settings_build.os == "Windows" and not environ.get("CONAN_BASH_PATH"):
            from conan.tools.build import build_jobs
            make_program = self._conanfile.conf.get("tools.gnu:make_program",
                                                    default="mingw32-make" if self._use_win_mingw() else "make")
            str_args = self._make_args
            str_extra_args = " ".join(args) if args is not None else ""
            jobs = ""
            if "-j" not in str_args and "nmake" not in make_program.lower():
                njobs = build_jobs(self._conanfile)
                if njobs:
                    jobs = "-j{}".format(njobs)
            command = " ".join(filter(None, [make_program, target, str_args, str_extra_args, jobs]))
            with vcvars(self._conanfile) if is_msvc(self._conanfile) else no_op():
                self._conanfile.run(f". {_env_activate_sh_path(self._conanfile)} && {command}", run_environment=True, win_bash=True)
        else:
            super(AutotoolsWinBash, self).make(target=target, args=args)


required_conan_version = ">=1.50.0"


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "configure.ac", "config.h.in", "Makefile.in", "test_package_c.c", "test_package_cpp.cpp",
    generators = "AutotoolsDeps", "AutotoolsToolchain", "VirtualBuildEnv"
    win_bash = True
    test_type = "explicit"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not environ.get("CONAN_BASH_PATH"):
            self.tool_requires("msys2/cci.latest")
        self.tool_requires(self.tested_reference_str)

    def build(self):
        for src in self.exports_sources:
            shutil.copy(path.join(self.source_folder, src), self.build_folder)

        self.run(f". {_env_activate_sh_path(self)} && autoconf --verbose", run_environment=True, win_bash=self._settings_build.os == "Windows")

        # Workaround for conan-io/conan#11975
        autotools = AutotoolsWinBash(self)
        autotools.configure()
        autotools.make()

    def test(self):
        if not cross_building(self):
            ext = ".exe" if self.settings.os == "Windows" else ""

            # Workaround for conan-io/conan#11975
            from conans.client.subsystems import subsystem_path
            test_cmd = subsystem_path(_subsystem(self), path.join(self.build_folder, f"test_package{ext}"))

            self.run(test_cmd, run_environment=True, win_bash=self.settings.os == "Windows")
