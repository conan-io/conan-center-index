from conans import ConanFile, tools, AutoToolsBuildEnvironment
import contextlib
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "configure.ac", "Makefile.am", "test_package.c"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        self.build_requires("automake/1.16.4")

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self):
                env = {
                    "AR": "{} lib".format(tools.microsoft.unix_path(self, os.path.join(self.build_folder, "build-aux", "ar-lib"))),
                    "CC": "cl -nologo",
                    "CXX": "cl -nologo",
                    "LD": "link -nologo",
                    "NM": "dumpbin -symbols",
                    "OBJDUMP": ":",
                    "RANLIB": ":",
                    "STRIP": ":",
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def build(self):
        for src in self.exports_sources:
            shutil.copy(os.path.join(self.source_folder, src), dst=os.path.join(self.build_folder, src))
        with tools.files.chdir(self, self.build_folder):
            for fn in ("COPYING", "NEWS", "INSTALL", "README", "AUTHORS", "ChangeLog"):
                tools.files.save(self, fn, "\n")
            with tools.run_environment(self):
                self.run("gnulib-tool --list", win_bash=tools.os_info.is_windows, run_environment=True)
                self.run("gnulib-tool --import getopt-posix", win_bash=tools.os_info.is_windows, run_environment=True)
            # m4 built with Visual Studio does not support executing *nix utils (e.g. `test`)
            with tools.environment_append({"M4":None}) if self.settings.os == "Windows" else tools.no_op():
                self.run("{} -fiv".format(os.environ["AUTORECONF"]), win_bash=tools.os_info.is_windows, run_environment=True)

            with self._build_context():
                autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
                autotools.configure()
                autotools.make()

    def test(self):
        if not tools.build.cross_building(self, self):
            bin_path = os.path.join(".", "test_package")
            self.run(bin_path, run_environment=True)
