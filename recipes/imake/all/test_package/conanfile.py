from conans import AutoToolsBuildEnvironment, ConanFile, tools
import contextlib
import os
import shutil

required_conan_version = ">=1.36.0"


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    test_type = "build_requires"

    exports_sources = "Imakefile", "Imake.tmpl"

    def build_requirements(self):
        if not tools.get_env("CONAN_MAKE_PROGRAM"):
            self.build_requires("make/4.2.1")

    @property
    def _settings_build(self):
        return self.settings_build if hasattr(self, "settings_build") else self.settings

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
        with self._build_context():
            self.run("imake", run_environment=True)

    def test(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.make()
