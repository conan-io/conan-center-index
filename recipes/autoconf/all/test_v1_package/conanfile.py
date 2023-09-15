from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conan.tools.files import copy
from conan.tools.microsoft import is_msvc
import contextlib
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
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
        for src in ("configure.ac", "config.h.in", "Makefile.in", "test_package_c.c", "test_package_cpp.cpp"):
            copy(self, src, os.path.join(self.source_folder, os.pardir, "test_package"), self.build_folder)
        self.run("autoconf --verbose", win_bash=tools.os_info.is_windows)
        self.run("{} --help".format(os.path.join(self.build_folder, "configure").replace("\\", "/")),
                 win_bash=tools.os_info.is_windows)
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        if is_msvc(self):
            autotools.flags.append("-FS")
        with self._build_context():
            autotools.configure()
            autotools.make()

    def test(self):
        if not tools.cross_building(self):
            self.run(os.path.join(".", "test_package"), run_environment=True)
