import shutil

from os import environ, path

from conan import ConanFile
from conan.tools.gnu import Autotools
from conan.tools.build import cross_building


def win_bash_configure(self, build_script_folder=None, args=None):
    # Workaround for conan-io/conan#11975
    # Duck typing configure and make methods, to skip calling the `subsystem` conf
    from conans.tools import args_to_string
    from conans.client.subsystems import subsystem_path
    script_folder = path.join(self._conanfile.source_folder, build_script_folder) \
        if build_script_folder else self._conanfile.source_folder

    configure_args = []
    configure_args.extend(args or [])

    self._configure_args = "{} {}".format(self._configure_args, args_to_string(configure_args))

    configure_cmd = "{}/configure".format(script_folder)
    if self._conanfile._settings_build.os == "Windows" and not environ.get("CONAN_BASH_PATH"):
        subsystem = "msys"
    else:
        subsystem = None
    configure_cmd = subsystem_path(subsystem, configure_cmd)
    cmd = '"{}" {}'.format(configure_cmd, self._configure_args)
    self._conanfile.output.info("Calling:\n > %s" % cmd)
    self._conanfile.run('"{}" {}'.format(subsystem_path(subsystem, path.join(self._conanfile.build_folder, "configure")), self._configure_args), run_environment=True, win_bash=self._conanfile._settings_build.os == "Windows")


def win_bash_make(self, target=None, args=None):
    # Workaround for conan-io/conan#11975
    # Duck typing configure and make methods, to skip calling the `subsystem` conf
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
    self._conanfile.run(command, run_environment=True, win_bash=self._conanfile._settings_build.os == "Windows")


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
        self.tool_requires(self.tested_reference_str)
        if self._settings_build.os == "Windows" and not environ.get("CONAN_BASH_PATH"):
            self.tool_requires("msys2/cci.latest")
            # Workaround for conan-io/conan#11975
            # Duck typing configure and make methods, to skip calling the `subsystem` conf
            Autotools.configure = win_bash_configure
            Autotools.make = win_bash_make

    def build(self):
        for src in self.exports_sources:
            shutil.copy(path.join(self.source_folder, src), self.build_folder)

        self.run("autoconf --verbose", run_environment=True, win_bash=self._settings_build.os == "Windows")

        # Workaround for conan-io/conan#11975
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def test(self):
        if not cross_building(self):
            ext = ".exe" if self.settings.os == "Windows" else ""
            self.run(path.join(self.build_folder, f"test_package{ext}"),  run_environment=True, win_bash=self.settings.os == "Windows")
