import shutil
from os import environ, path

from conan import ConanFile
from conan.tools.gnu import Autotools
from conan.tools.build import cross_building

required_conan_version = ">=1.50.0"


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "configure.ac", "config.h.in", "Makefile.in", "test_package_c.c", "test_package_cpp.cpp",
    generators = "AutotoolsDeps", "AutotoolsToolchain", "VirtualBuildEnv"
    win_bash = True
    test_type = "explicit"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)
        if self._settings_build.os == "Windows" and not environ.get("CONAN_BASH_PATH"):
            self.tool_requires("msys2/cci.latest")

    def build(self):
        for src in self.exports_sources:
            shutil.copy(path.join(self.source_folder, src), self.build_folder)

        self.run("autoconf --verbose", run_environment=True, win_bash=self.settings.os == "Windows")
        self.run("{} --help".format(path.join(self.build_folder, "configure").replace("\\", "/")), run_environment=True, win_bash=self.settings.os == "Windows")

        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def test(self):
        if not cross_building(self):
            self.run(path.join(".", "test_package"), run_environment=True, win_bash=self.settings.os == "Windows")
