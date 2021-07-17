from conans import AutoToolsBuildEnvironment, ConanFile
import os
import shutil

required_conan_version = ">=1.36.0"


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    test_type = "build_requires"

    exports_sources = "Imakefile", "Imake.tmpl"

    @property
    def _settings_build(self):
        return self.settings_build if hasattr(self, "settings_build") else self.settings

    def build(self):
        for src in self.exports_sources:
            shutil.copy(os.path.join(self.source_folder, src), os.path.join(self.build_folder, src))
        self.run("imake", run_environment=True)

    def test(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=self._settings_build.os == "Windows")
        autotools.make()
