from conans import ConanFile, tools, AutoToolsBuildEnvironment
from contextlib import contextmanager
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "configure.ac", "Makefile.am", "test_package.c"

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH") and \
                tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")
        self.build_requires("automake/1.16.1")

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                env = {
                    "AR": "{} lib".format(tools.unix_path(os.path.join(self.build_folder, "build-aux", "ar-lib"))),
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
        with tools.chdir(self.build_folder):
            for fn in ("COPYING", "NEWS", "INSTALL", "README", "AUTHORS", "ChangeLog"):
                tools.save(fn, "\n")
            self.run("gnulib-tool --list", win_bash=tools.os_info.is_windows)
            self.run("gnulib-tool --import getopt-posix", win_bash=tools.os_info.is_windows)
            self.run("{} -ifv".format(os.environ["AUTORECONF"]), win_bash=tools.os_info.is_windows)

            with self._build_context():
                autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
                autotools.configure()
                autotools.make()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join(".", "test_package")
            self.run(bin_path, run_environment=True)
