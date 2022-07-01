from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conan.tools.microsoft import is_msvc
import contextlib
import os
import shutil

required_conan_version = ">=1.45.0"


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "configure.ac", "config.h.in", "Makefile.in", "test_package_c.c", "test_package_cpp.cpp",
    test_type = "explicit"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        self.build_requires(self.tested_reference_str)
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    @contextlib.contextmanager
    def _build_context(self):
        if is_msvc(self):
            with tools.vcvars(self):
                with tools.environment_append({"CC": "cl -nologo", "CXX": "cl -nologo",}):
                    yield
        else:
            yield

    def build(self):
        for src in self.exports_sources:
            shutil.copy(os.path.join(self.source_folder, src), self.build_folder)
        self.run("{} --verbose".format(os.environ["AUTOCONF"]),
                 win_bash=tools.os_info.is_windows, run_environment=True)
        self.run("{} --help".format(os.path.join(self.build_folder, "configure").replace("\\", "/")),
                 win_bash=tools.os_info.is_windows, run_environment=True)
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        with self._build_context():
            autotools.configure()
            autotools.make()

    def test(self):
        if not tools.cross_building(self):
            self.run(os.path.join(".", "test_package"), run_environment=True)
