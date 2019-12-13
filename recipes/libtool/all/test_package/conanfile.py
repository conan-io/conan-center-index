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

    def requirements(self):
        self.requires("automake/1.16.1")

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
        self.run("autoreconf --verbose --install --force", win_bash=tools.os_info.is_windows)

        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.configure()
        autotools.make()

    def test(self):
        self.run(os.path.join(".", "test_package"), run_environment=True)
