from conans import AutoToolsBuildEnvironment, ConanFile, tools
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "configure.ac", "Makefile.am",
    generators = "pkg_config"
    test_type = "explicit"

    @property
    def _settings_build(self):
        return self.settings_build if hasattr(self, "settings_build") else self.settings

    def build_requirements(self):
        self.build_requires(self.tested_reference_str)
        self.build_requires("automake/1.16.3")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def build(self):
        for src in self.exports_sources:
            shutil.copy(os.path.join(self.source_folder, src), self.build_folder)
        print(tools.get_env("AUTOMAKE_CONAN_INCLUDES"))
        self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=self._settings_build.os == "Windows", run_environment=True)
        autotools = AutoToolsBuildEnvironment(self, win_bash=self._settings_build.os == "Windows")
        autotools.configure()

    def test(self):
        # FIXME: how to test extra pkg_config content?
        pass
