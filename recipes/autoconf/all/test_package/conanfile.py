import shutil
from os import path

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.gnu import Autotools
from conan.tools.microsoft import unix_path

required_conan_version = ">=1.50.0"


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "configure.ac", "config.h.in", "Makefile.in", "test_package_c.c", "test_package_cpp.cpp",
    generators = "AutotoolsDeps", "AutotoolsToolchain", "VirtualBuildEnv"
    test_type = "explicit"

    @property
    def _settings_build(self):
        # TODO: Remove for Conan v2
        return getattr(self, "settings_build", self.settings)

    @property
    def win_bash(self):
        return self._settings_build.os == "Windows"

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", default=False, check_type=bool):
            self.tool_requires("msys2/cci.latest")  # The conf `tools.microsoft.bash:path` and `tools.microsoft.bash:subsystem` aren't injected for test_package
        self.tool_requires(self.tested_reference_str)

    def build(self):
        if self._settings_build.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", default=False, check_type=bool):
            return  # autoconf needs a bash if there isn't a bash no need to build

        for src in self.exports_sources:
            shutil.copy(path.join(self.source_folder, src), self.build_folder)

        self.run(f"autoconf --verbose")

        autotools = Autotools(self)
        autotools.configure(build_script_folder=self.build_folder)
        autotools.make()

    def test(self):
        if self._settings_build.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", default=False, check_type=bool):
            return  # autoconf needs a bash if there isn't a bash no need to build

        if can_run(self):
            ext = ".exe" if self.settings.os == "Windows" else ""
            test_cmd = unix_path(self, path.join(self.build_folder, f"test_package{ext}"))

            self.run(test_cmd, run_environment=True)
