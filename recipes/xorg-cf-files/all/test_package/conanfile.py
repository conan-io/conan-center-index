from conans import AutoToolsBuildEnvironment, ConanFile, tools
import contextlib
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "Imakefile", "test_package.c"

    def build_requirements(self):
        self.build_requires("imake/1.0.8")
        if not tools.get_env("CONAN_MAKE_PROGRAM"):
            self.build_requires("make/4.3")

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
                self.run("imake -DUseInstalled -I{}".format(self.deps_user_info["xorg-cf-files"].CONFIG_PATH), run_environment=True)
        with self._build_context():
            autotools = AutoToolsBuildEnvironment(self)
            with tools.environment_append(autotools.vars):
                autotools.make(target="test_package")

    def test(self):
        if not tools.build.cross_building(self, self):
            self.run(os.path.join(".", "test_package"), run_environment=True)
