from conans import AutoToolsBuildEnvironment, ConanFile, tools
import contextlib
import os
import shutil

required_conan_version = ">=1.56.0"


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "configure.ac", "Makefile.am", "test_package.c"
    test_type = "explicit"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        self.build_requires(self.tested_reference_str)
        self.build_requires("automake/1.16.5")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self):
                env = {
                    "CC": "cl -nologo",
                    "CXX": "cl -nologo",
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def build(self):
        for src in self.exports_sources:
            shutil.copy(os.path.join(self.source_folder, src), self.build_folder)

        # Work around the fact that "used_special_vars" in conans/client/tools/win.py doesn't handle ACLOCAL_PATH
        aclocal_path = "$ACLOCAL_PATH:" + self.deps_env_info.vars["ACLOCAL_PATH"][0].lower()
        self.run("ACLOCAL_PATH={} autoreconf -fiv".format(aclocal_path), win_bash=self._settings_build.os == "Windows")
        with self._build_context():
            autotools = AutoToolsBuildEnvironment(self, win_bash=self._settings_build.os == "Windows")
            autotools.libs = []
            autotools.configure()
            autotools.make()

    def test(self):
        if not tools.cross_building(self):
            self.run(os.path.join(".", "test_package"))
