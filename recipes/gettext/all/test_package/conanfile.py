from conans import ConanFile, tools, AutoToolsBuildEnvironment
import contextlib
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler"
    exports_sources = "configure.ac",

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        self.build_requires("automake/1.16.3")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self):
                env = {
                    "CC": "cl -nologo",
                    "LD": "link -nologo",
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def build(self):
        for src in self.exports_sources:
            shutil.copy(os.path.join(self.source_folder, src), os.path.join(self.build_folder, src))

        self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)
        with self._build_context():
            autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            autotools.configure()

    def test(self):
        for exe in ["gettext", "ngettext", "msgcat", "msgmerge"]:
            self.run("{} --version".format(exe), run_environment=True)
