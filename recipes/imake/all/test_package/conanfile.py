from conans import AutoToolsBuildEnvironment, ConanFile, tools
import contextlib
import os
import shutil

required_conan_version = ">=1.36.0"


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    exports_sources = "Imakefile", "Imake.tmpl"

    def build_requirements(self):
        if not tools.get_env("CONAN_MAKE_PROGRAM"):
            self.build_requires("make/4.2.1")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self):
                env = {
                    "CC": "cl -nologo",
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def build(self):
        for src in self.exports_sources:
            shutil.copy(os.path.join(self.source_folder, src), os.path.join(self.build_folder, src))
        if not tools.build.cross_building(self, self):
            with self._build_context():
                self.run("imake", run_environment=True)

    def test(self):
        if not tools.build.cross_building(self, self):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.make()
