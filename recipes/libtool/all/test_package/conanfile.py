from conans import AutoToolsBuildEnvironment, ConanFile, tools
from contextlib import contextmanager
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "configure.ac", "Makefile.am", "test_package.c", "lib.c", "lib.h", "libtestlib.sym", "testlib_private.h"

    def build_requirements(self):
        if tools.os_info.is_windows and "CONAN_BASH_PATH" not in os.environ \
                and tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                with tools.environment_append({"CC": "cl -nologo", "CXX": "cl -nologo",}):
                    yield
        else:
            yield

    @property
    def _package_folder(self):
        return os.path.join(self.build_folder, "package")

    def build(self):
        for src in self.exports_sources:
            shutil.copy(os.path.join(self.source_folder, src), self.build_folder)
        self.run("{} --install --verbose -Wall".format(os.environ["AUTORECONF"]), win_bash=tools.os_info.is_windows)

        tools.mkdir(self._package_folder)
        conf_args = [
            "--prefix={}".format(tools.unix_path(self._package_folder)),
            "--enable-shared", "--enable-static",
        ]
        with self._build_context():
            autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            autotools.configure(args=conf_args)
            autotools.make(args=["V=1", "-j1"])
            autotools.install()

    def test(self):
        assert os.path.isdir(os.path.join(self._package_folder, "bin"))
        assert os.path.isfile(os.path.join(self._package_folder, "include", "lib.h"))
        assert os.path.isdir(os.path.join(self._package_folder, "lib"))

        if not tools.cross_building(self.settings):
            self.run(os.path.join(self._package_folder, "bin", "test_package"), run_environment=True)
