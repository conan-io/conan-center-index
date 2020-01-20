from conans import AutoToolsBuildEnvironment, ConanFile, tools
from contextlib import contextmanager
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "configure.ac", "Makefile.am", "test_package.c", "lib.c"

    def build_requirements(self):
        if tools.os_info.is_windows and "CONAN_BASH_PATH" not in os.environ:
            self.build_requires("msys2/20190524")

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                with tools.environment_append({"CC": "cl -nologo", "CXX": "cl -nologo",}):
                    yield
        else:
            with tools.no_op():
                yield

    def build(self):
        for src in self.exports_sources:
            shutil.copy(os.path.join(self.source_folder, src), self.build_folder)
        self.run("{} --verbose --install --force".format(os.environ["AUTORECONF"]), win_bash=tools.os_info.is_windows)

        with self._build_context():
            autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            autotools.configure()
            autotools.make()

    def test(self):
        exeext = ".exe" if self.settings.os == "Windows" else ""
        self.run(os.path.join(".", "test_package{}".format(exeext)), run_environment=True)
